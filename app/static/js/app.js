var myModal = angular.module('app', ['ui.bootstrap', 'angularMoment']);
myModal.controller('Ctrl', function ($scope, $http, $uibModal) {
    $scope.showReport = function(jobId) {

            $http.get('/detail/' + jobId)
                .success(function(response) {
                    var job = response.data;
                    var observable = {data: job.data, dataType: job.dataType}
                    var report = {
                        job: job,
                        template: job.analyzerName || job.analyzerId,
                        content: job.report,
                        status: job.status,
                        startDate: job.startDate,
                        endDate: job.endDate
                    };

                    var modalInstance = $uibModal.open({
                        templateUrl: '/static/reports/modal_template.html',
                        controller: 'JobReportModalCtrl',
                        controllerAs: '$vm',
                        size: 'lg',
                        resolve: {
                            report: function() {
                                return report
                            },
                            observable: function() {
                                return observable;
                            }
                        }
                    });

                });

    }

    });

myModal.controller('JobReportModalCtrl', function($uibModalInstance, report, observable) {
        this.report = report;
        this.observable = observable;
        this.close = function() {
            $uibModalInstance.dismiss();
        }
    });

myModal.directive('report', function ($templateRequest, $q, $compile) {
            function updateReport(a, b, scope) {
                if (!angular.isDefined(scope.content) || !angular.isDefined(scope.name)) {
                    scope.element.html('');
                    return;
                }

                $templateRequest('/static/reports/thehive-templates/' + scope.name + '/long.html', true)
                    .then(function (tmpl) {
                        scope.element.html($compile(tmpl)(scope));
                    });
            }
            return {
                restrict: 'E',
                scope: {
                    name: '=',
                    artifact: '=',
                    reportType: '@',
                    status: '=',
                    content: '=',
                    success: '='
                },
                link: function (scope, element) {
                    scope.element = element;
                    scope.$watchGroup(['name', 'content', 'status'], updateReport);
                }
            };
        });