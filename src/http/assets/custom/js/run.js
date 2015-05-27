/* Handles the log messages received on the websocket. */
function LogView($viewContainer) {
    var self = this;
    self._$viewContainer = $viewContainer;
    self._$logOutput = self._$viewContainer.find(".log-output");
    self.initialize = function (initMessage) {
        self._$logOutput.html(initMessage || '===== LOG SYSTEM STARTED =====');
        self._$logOutput.append('<br>');
    }

    self.onLogMessage = function (message) {
        self._$logOutput.append(message + '<br>');
        self._$logOutput.scrollTop(self._$logOutput[0].scrollHeight);
    }
}

function RunUI($uiContainer) {
    var self = this;

    self._$uiContainer = $uiContainer;
    self._selectizeSolver = null;
    self._solversById = {};
    self._problemsById = {};

    self._solverForm = null;
    self._solverFormModal = null;

    self._solverIsRunning = false;
    self._webSocket = null;

    self._logView = null;

    self._retrieveSolvers = function () {
        self._selectizeSolver.clear();
        self._selectizeSolver.clearOptions();
        self._solversById = {};
        $.ajax({
            url: '/api/solvers/list',
            dataType: 'json',
            success: function (results) {
                for (var i = 0; i < results.length; i++) {
                    var solver = results[i];
                    self._selectizeSolver.addOption({
                        text: solver.name,
                        value: solver._id
                    });
                    self._solversById[solver._id] = solver
                };
            },
            error: function (e) {
                console.error(e);
                $.UIkit.notify("An error occurred while retrieving the existing solvers. See logs for details.", {status: 'danger'});
            }
        })
    }


    self._retrieveProblems = function () {
        $.ajax({
            url: '/api/problems/list',
            dataType: 'json',
            success: function (results) {
                for (var i = 0; i < results.length; i++) {
                    self._problemsById[results[i]._id] = results[i]
                };
            }
        })
    }

    self._onSocketMessage = function (evt) {
        var data = JSON.parse(evt.data);
        if (data.log) {
            self._logView.onLogMessage(data.log);
        }
    }

    self.initialize = function () {
        self._$uiContainer.find('#select-solver').selectize({
            create: true,
            onItemAdd: self.onSolverSelect
        });
        self._selectizeSolver = self._$uiContainer.find('#select-solver')[0].selectize;

        self._solverForm = new SolverForm($('#create-solver-modal .uk-modal-dialog'), {
            saved: self.onCreateSolver
        });
        self._retrieveSolvers();
        self._retrieveProblems();
        self._solverForm.initialize();
        self._solverFormModal = $.UIkit.stackableModal('#create-solver-modal');

        self._$uiContainer.find('#run-solver').click(self.onRun);

        self._logView = new LogView($('#log-panel'));
    }

    self.onSolverSelect = function (value, data) {
        if (!(value in self._solversById)) {
            console.log("Create solver: ", value, data);
            self._solverForm.prefill({
                name: value
            });
            self._selectizeSolver.clear();
            self._selectizeSolver.removeOption(value);
            self._solverFormModal.show();
        }
        else {
            var solver = self._solversById[value];
            self._$uiContainer.find('#solver-description').html(
                '<span class="uk-text-primary uk-text-bold">Name</span>: <em>"' + solver.name +
                '"</em> ; <span class="uk-text-primary uk-text-bold">Type</span>: <em>"' + solver.type +
                '"</em>; <span class="uk-text-primary uk-text-bold">Implementation</span>: <em>"' + solver.implementation +
                '"</em>; <span class="uk-text-primary uk-text-bold">Parameters</span>: ');
            for (var p in solver.parameters)
                self._$uiContainer.find('#solver-description').append(
                    '<span class="uk-text-success">' + p + '</span>=<em>"' + solver.parameters[p] + '"</em> ');
            var problem = self._problemsById[solver.problemId];
            self._$uiContainer.find('#solver-description').append(
                '<br><span class="uk-text-large sep">Solving</span><br>' +
                '<span class="uk-text-primary uk-text-bold">Name</span>: <em>"' + problem.name +
                '"</em> ; <span class="uk-text-primary uk-text-bold">Type</span>: <em>"' + problem.types.join(',') +
                '"</em>; <span class="uk-text-primary uk-text-bold">Implementation</span>: <em>"' + problem.implementation +
                '"</em>; <span class="uk-text-primary uk-text-bold">Parameters</span>: ');
            for (var p in problem.parameters)
                self._$uiContainer.find('#solver-description').append(
                    '<span class="uk-text-success">' + p + '</span>=<em>"' + problem.parameters[p] + '"</em> ');
        }
    }

    self.onCreateSolver = function (solverData) {
        console.log("Solver created: ", solverData);
        self._solverFormModal.hide();
        self._selectizeSolver.addOption({
            text: solverData.name,
            value: solverData._id
        });
        self._solversById[solverData._id] = solverData;
        self._selectizeSolver.addItem(solverData._id);
    }

    // note: this function will only be called once the web-socket connection has been initialized.
    self.onRun = function () {
        self._webSocket = new WebSocket('ws://localhost:5000/api/run/');
        self._webSocket.onmessage = self._onSocketMessage
        self._webSocket.onopen = function () {
            self._logView.initialize();
            var solverId = self._selectizeSolver.getValue();
            if (!solverId.trim()) {
                $.UIkit.notify("No solver was specified to be run!", {status: 'danger'});
                return self._selectizeSolver.$control.addClass('invalid');
            }
            else
                self._selectizeSolver.$control.removeClass('invalid');
            self._webSocket.send(JSON.stringify({
                action: 'run',
                solver: solverId
            }));
        };
    }
}
