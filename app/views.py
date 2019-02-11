from flask import render_template, flash, jsonify
from app import app
from .forms import IocForm, FileForm
from config import DATA_TYPES, CORTEX, CORTEX_API
import requests
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import pprint


def _get_analyzers(data_type):
    analyzers = {}
    headers = {'Authorization': 'Bearer %s' % CORTEX_API}
    try:
        r = requests.get('%s/api/analyzer/type/%s' % (CORTEX, data_type), headers=headers)
        analyzer_json = r.json()
        for a in analyzer_json:
            analyzers[a['name']] = a['_id']
    except Exception:
        pass

    return analyzers


def _run_analyzers(ioc, analyzers, data_type):
    headers = {'Authorization': 'Bearer %s' % CORTEX_API}
    success = 0
    try:
        j_data = {"data":ioc, "dataType": data_type, "tlp":0 }
        for analyzer in analyzers:
            r = requests.post('%s/api/analyzer/%s/run?force=1' % (CORTEX, analyzer), headers=headers, json=j_data)
            analyzer_response = r.json()
            if 'errors' not in analyzer_response:
                success += 1
    except Exception:
        pass

    return success


def _run_file_analyzers(file_path, analyzers):
    headers = {'Authorization': 'Bearer %s' % CORTEX_API}
    success = 0
    try:
        j_data = json.dumps({"dataType": "file", "tlp":0})
        f_data = {'attachment': open(file_path, 'rb'), '_json': (None, j_data, 'application/json')}
        for analyzer in analyzers:
            r = requests.post('%s/api/analyzer/%s/run?force=1' % (CORTEX, analyzer), headers=headers, files=f_data)
            analyzer_response = r.json()
            print analyzer_response
            if 'errors' not in analyzer_response:
                success += 1
    except Exception:
        pass

    return success


def _get_jobs(observable=None):
    jobs = {}
    headers = {'Authorization': 'Bearer %s' % CORTEX_API}
    try:
        if observable:
            q = {"query": { "_field": "data", "_value": observable}}
            q2 = {"query": {'_field': 'attachment.name', '_value': observable}}
            r = requests.post('%s/api/job/_search?range=all' % CORTEX, headers=headers, json=q)
            r2 = requests.post('%s/api/job/_search?range=all' % CORTEX, headers=headers, json=q2)
            jobs = r.json() + r2.json()
        else:
            r = requests.post('%s/api/job/_search?range=all' % CORTEX, headers=headers, data = {'range':'all'})
            jobs = r.json()
    except Exception:
        print 'hit exception'
        pass
    return jobs


def _get_job_detail(job_id):
    job = {}
    headers = {'Authorization': 'Bearer %s' % CORTEX_API}
    try:
        r = requests.get('%s/api/job/%s/report' % (CORTEX, job_id), headers=headers)
        job = r.json()
    except Exception:
        print 'hit exception'
        pass
    return job


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    jobs = _get_jobs()

    summary = {}
    for job in jobs:
        if not job['status'] == 'Success':
            continue
        jdt = datetime.fromtimestamp(job['date'] / 1000)
        ioc = job.get('data') or job['attachment']['name']
        if ioc in summary:
            summary[ioc]['count'] += 1
            if jdt < summary[ioc]['first_seen']:
                summary[ioc]['first_seen'] = jdt
            if jdt > summary[ioc]['last_seen']:
                summary[ioc]['last_seen'] = jdt
        else:
            summary[ioc] = {'first_seen': jdt, 'last_seen': jdt, 'count': 1}

    order = sorted(summary.keys(), key=lambda x: (summary[x]['last_seen']))

    return render_template('index.html', title='Observable Reports', summary=summary, order=reversed(order))


@app.route('/reports/<observable>', methods=['GET', 'POST'])
def reports(observable):
    jobs = _get_jobs(observable)
    pprint.pprint(jobs[0])
    for job in jobs:
        job['createdAt'] = datetime.fromtimestamp(job['date'] / 1000)
    return render_template('observable_reports.html', title='Observable Reports', jobs=jobs)


@app.route('/artifacts/<observable>', methods=['GET', 'POST'])
def artifacts(observable):
    jobs = _get_jobs(observable)
    results = []
    for job in jobs:
        det = _get_job_detail(job.get('id', ''))
        job_artifacts = det.get('report', {}).get('artifacts', [])
        if len(job_artifacts) < 1:
            continue

        for a in job_artifacts:
            a['analyzerName'] = job['analyzerName']
            a['date'] = datetime.fromtimestamp(job['date'] / 1000)
        results += job_artifacts
        print results

    return render_template('artifacts.html', title='Artifacts From Analysis: %s' % observable, artifacts=results)


@app.route('/query/<data_type>', methods=['GET', 'POST'])
def query(data_type):
    if not (data_type in DATA_TYPES):
        raise Exception("Bad Values")
    if data_type == 'file':
        form = FileForm()
    else:
        form = IocForm()
    form.data_type = data_type
    analyzers = _get_analyzers(data_type)
    print analyzers
    print list([(k, v) for k,v in analyzers.iteritems()])
    form.analyzers.choices = [(v, k) for k,v in analyzers.iteritems()]

    if form.validate_on_submit():
        picked_analyzers = form.analyzers.data
        if data_type == 'file':
            fname = secure_filename(form.value.data.filename)
            form.value.data.save('/tmp/' + fname)
            file_path = '/tmp/' + fname
            results = _run_file_analyzers(file_path, picked_analyzers)
        else:
            ioc = form.value.data

            misp = form.misp.data
            results = _run_analyzers(ioc, picked_analyzers, data_type)

        flash('Successfully submitted %s analyzers' % results)

    return render_template('query.html', title='Edit/View Referers', form=form)


@app.route('/detail/<job_id>', methods=['GET', 'POST'])
def detail(job_id):
    job = _get_job_detail(job_id)

    return jsonify({'data': job})