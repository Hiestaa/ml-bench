function RunUI($uiContainer) {
    var self = this;

    self._$uiContainer = $uiContainer;
    self._selectizeSolver = null;
    self._solversById = {};

    self._solverForm = null;
    self._solverFormModal = null;

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
        self._solverForm.initialize();
        self._solverFormModal = $.UIkit.stackableModal('#create-solver-modal');
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
    }

    self.onCreateSolver = function (solverData) {
        console.log("Solver created: ", solverData);
        self._solverFormModal.hide();
        self._selectizeSolver.addOption({
            text: solverData.name,
            value: solverData._id
        });
        self._selectizeSolver.addItem(solverData._id);
        self._solversById[solverData._id] = solverData;
    }
}
