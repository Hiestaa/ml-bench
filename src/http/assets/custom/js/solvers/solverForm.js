var default_event = function () {
    console.log("Default event fired with arguments:", arguments);
}
/*
Instanciates an object able to manipulate the solver form.
* `$container`: jquery elements that contains the actual solver form
* `events`: (optional) an object containing events related to the form. This includes:
    * `saved`:function(solverData) fired when the a solver has been saved (either created or updated)
*/
function SolverForm($container, events) {
    var self = this;

    self._$formContainer = $container;
    self._$form = $container.find('.solver-form');
    self._implementations = null;
    self._problemsBySolverType = null;
    self._parameterTemplate = '\
<div class="uk-width-1-1 uk-width-medium-1-2 uk-width-large-1-3 parameter-field">\
    <label class="uk-form-label" for="input-{{name}}">{{name}}</label>\
    <input type="text" id="input-param-{{name}}" placeholder="{{name}}" class="uk-width-1-1" value="{{value}}">\
<div>\
';
    self._selectizeType = null;
    self._selectizeImplem = null;
    self._selectizeProblem = null;
    self._selectizeVisualization = null;
    self._currentSolver = null;

    self._problemFormModal = null;
    self._problemForm = null;

    if (!events)
        events = {}
    self._events = {
        saved: events.saved || default_event
    }

    self.prefill = function (prefill) {
        if (prefill && prefill.name)
            self._$form.find('#input-name').val(prefill.name);
        if (prefill && prefill.type)
            self._selectizeType.addItem(prefill.type);
    }

    self._retrieveProblems = function () {
        $.ajax({
            url: '/api/problems/list',
            dataType: 'json',
            success: function (results) {
                self._problemsBySolverType = {
                    'optimizer': [],
                    'clusterer': [],
                    'classifier': []
                }
                for (var i = 0; i < results.length; i++) {
                    if (results[i].types.indexOf('optimization') > -1)
                        self._problemsBySolverType['optimizer'].push(results[i])
                    if (results[i].types.indexOf('clustering') > -1)
                        self._problemsBySolverType['clusterer'].push(results[i])
                    if (results[i].types.indexOf('classification') > -1)
                        self._problemsBySolverType['classifier'].push(results[i])
                };
            }
        })
    }

    self._retrieveImplems = function (onSuccess) {
        // onSuccess will be called when the implems have been retrieved
        $.ajax({
            url: '/api/solvers/implementations',
            dataType: 'json',
            success: function (results) {
                self._implementations = results;
                self._selectizeType.clearOptions();
                for (var type in self._implementations) {
                    self._selectizeType.addOption({
                        value: type,
                        text: type
                    });
                };
                if (onSuccess)
                    onSuccess();
            },
            error: function (error) {
                console.error(error);
                $.UIkit.notify("An error occurred while retrieving the available implementations, see logs for details", {status:'danger'})
            }
        });
    }

    /*
    The form can be initilized given a solver, in which case
    this solver will be displayed in the form, ready to be updated.
    */
    self.initialize = function (solver) {
        self._$form.find('#select-type').selectize({
            onItemAdd: self.onSelectType,
            onClear: self.onClearSelectType
        });
        self._$form.find('#select-implem').selectize({
            onItemAdd: self.onSelectImplem,
            onClear: self.onClearSelectImplem
        });
        self._$form.find('#select-problem').selectize({
            create: true,
            onItemAdd: self.onProblemSelect
        });
        self._$form.find('#select-visualization').selectize({});
        self._selectizeType = self._$form.find('#select-type')[0].selectize;
        self._selectizeImplem = self._$form.find('#select-implem')[0].selectize;
        self._selectizeProblem = self._$form.find('#select-problem')[0].selectize;
        self._selectizeVisualization = self._$form.find('#select-visualization')[0].selectize;

        self._$form.find('#reset').click(self.onReset);
        self._$form.find('#submit').click(self.onSubmit);
        self._$form.find('#clear').click(self.onClear);

        self._retrieveProblems();
        self._retrieveImplems(function () {
            if (solver)
                self.setSolver(solver)
        });

        self._problemForm = new ProblemForm($('#create-problem-modal .uk-modal-dialog'), {
            saved: self.onCreateProblem
        });
        self._problemForm.initialize();
        self._problemFormModal = $.UIkit.stackableModal('#create-problem-modal');
    }

    self.onSelectType = function (type) {
        self._selectizeImplem.clearOptions();
        self._selectizeImplem.clear();
        self._selectizeProblem.clearOptions();
        self._selectizeProblem.clear();
        var added = false;
        for (var implem in self._implementations[type]) {
            if (implem === undefined)
                break;
            self._selectizeImplem.addOption({
                text: implem,
                value: implem
            });
            if (!added) {
                self._selectizeImplem.addItem(implem);
                added = true;
            }
        }
        added = false;
        for (var pid = 0; pid < self._problemsBySolverType[type].length; pid++) {
            var problem = self._problemsBySolverType[type][pid];
            self._selectizeProblem.addOption({
                text: problem.name,
                value: problem._id
            });
            if (!added) {
                self._selectizeProblem.addItem(problem._id);
                added = true;
            }
        }
    }

    self.onSelectImplem = function (implem) {
        var selectedType = null;
        var classObj = null;
        self._$form.find('#description').html('Select an implementation to view its description here...');
        self._$form.find('#parameters').html('');
        if (!implem) {
            return;
        }
        selectedType = self._selectizeType.getValue();
        classObj = self._implementations[selectedType][implem];
        self._$form.find('#description').html(
            formatDoc(classObj.description));
        for (var parameter in classObj.parameters) {
            self._$form.find('#parameters').append(
                render(self._parameterTemplate, {
                    name: parameter,
                    value: classObj.parameters[parameter]
                }));
        };
    }

    self.onClearSelectType = function () {
        self._selectizeImplem.clear();
    }

    self.onClearSelectImplem = function () {
        self._$form.find('#description').html('Select an implementation to view its description here...');
        self._$form.find('#parameters').html('');
    }

    self.setSolver = function (solver) {
        console.log("Setting solver:", solver);
        self._selectizeType.clear();
        self._selectizeImplem.clear();
        self._selectizeProblem.clear();
        self._selectizeVisualization.clear();

        if (!self._implementations)
            return $.UIkit.notify("The existing implementations have not been loaded yet. Please try again later.", {status: 'danger'});
        // a solver may have more than one type. Select the first one
        // that is linked to the solver's implementation.
        var typeToDisplay = null;
        for (var type in self._implementations) {
            if (typeToDisplay !== null)
                break;
            if (solver.type == type) {
                for (var implem in self._implementations[type]) {
                    if (solver.implementation == implem) {
                        typeToDisplay = type;
                        break;
                    }
                }
            }
        }
        if (typeToDisplay == null)
            return $.UIkit.notify("The solver's implementation does not exist anymore. You should delete and re-created it.", {status: 'danger'});
        // add the type and implementation of this solver to the selectize boxes
        self._selectizeType.addItem(typeToDisplay);
        self._selectizeImplem.addItem(implem);

        // fill in the name of the solver
        self._$form.find('#input-name').val(solver.name);

        // fill in the parameters values
        for (var param_name in solver.parameters) {
            var input = self._$form.find('#input-param-' + param_name);
            if (input.length == 0)
                return $.UIkit.notify('The parameter named `' + param_name + "' does not exist for this implementation!", {status: 'danger'})
            input.val(solver.parameters[param_name]);
        }

        // save current solver to be able to reset the form.
        self._currentSolver = solver;
    }

    self.validate = function () {
        // return true if all required fields are validated.
        var valid = true;
        // type select
        if (!self._selectizeType.getValue().trim()) {
            self._selectizeType.$control.addClass('invalid');
            valid = false;
        }
        else {
            self._selectizeType.$control.removeClass('invalid');
        }
        // implem select
        if (!self._selectizeImplem.getValue().trim()) {
            self._selectizeImplem.$control.addClass('invalid');
            valid = false;
        }
        else {
            self._selectizeImplem.$control.removeClass('invalid');
        }
        // problem select
        if (!self._selectizeProblem.getValue().trim()) {
            self._selectizeProblem.$control.addClass('invalid');
            valid = false;
        }
        else {
            self._selectizeProblem.$control.removeClass('invalid');
        }
        // name input
        if (!self._$form.find('#input-name').val().trim()) {
            self._$form.find('#input-name').addClass('invalid');
            valid = false;
        }
        else {
            self._$form.find('#input-name').removeClass('invalid')
        }
        // parameters (cannot be checked if no implem has been defined)
        if (!self._selectizeImplem.getValue().trim())
            return valid;
        classObj = self._implementations[self._selectizeType.getValue()][self._selectizeImplem.getValue()];
        for (var i = 0; i < classObj.parameters.length; i++) {
            var param_name = classObj.parameters[i];
            if (!self._$form.find('#input-param-' + param_name).val()) {
                self._$form.find('#input-param-' + param_name).addClass('invalid');
                valid = false;
            }
            else {
                self._$form.find('#input-param-' + param_name).removeClass('invalid');
            }
        }
        return valid;
    }

    self.onSubmit = function () {
        var data = {}
        var classObj = null;

        if (!self.validate()) {
            return $.UIkit.notify('Some required fields have not be filled in. Please fill the fields marked in red then submit the form again.', {status: 'warning'});
        }
        console.log("Submitting form");

        data.name = self._$form.find('#input-name').val();
        data.implementation = self._selectizeImplem.getValue();
        data.problem = self._selectizeProblem.getValue();
        data.visualization = self._selectizeVisualization.getValue();

        data.parameters = {}
        classObj = self._implementations[self._selectizeType.getValue()][data.implementation];
        for (var param_name in classObj.parameters) {
            data.parameters[param_name] = self._$form.find('#input-param-' + param_name).val();
        }
        data.parameters = JSON.stringify(data.parameters);

        if (self._currentSolver !== null)
            data._id = self._currentSolver._id;

        $.ajax({
            url: '/api/solvers/save',
            type: 'post',
            dataType: 'json',
            data: data,
            success: function (data) {
                $.UIkit.notify('The solver ' + data.name + ' has successfully been saved!');
                self._currentSolver = null;
                self.onReset();
                self._events.saved(data);
            },
            error: function (error) {
                console.error(error);
                $.UIkit.notify("An error occurred while saving the solver: " + data.name, {status: 'danger'});
            }
        })
    }

    self.onReset = function () {
        console.log("Resetting form");
        if (self._currentSolver)
            return self.setSolver(self._currentSolver);
        // clear items only, not options
        self._selectizeType.clear();
        self._selectizeImplem.clear();
        self._selectizeProblem.clear();
        self._selectizeVisualization.clear();
        self._$form.find('#input-name').val('');
        self._$form.find('#description').html('Select an implementation to view its description here...');
        self._$form.find('#parameters').html('');
        self._$form.find('#input-name').removeClass('invalid');
        self._selectizeType.$control.removeClass('invalid');
        self._selectizeProblem.$control.removeClass('invalid');
        self._selectizeImplem.$control.removeClass('invalid');
    }

    self.onClear = function () {
        self._currentSolver = null;
        self.onReset();
    }

    self.onProblemSelect = function (value, data) {
        var selected_type = self._selectizeType.getValue();
        if (!selected_type || !self._problemsBySolverType[selected_type].find(function (item) {
            return item._id == value
        })) {
            console.log("Create problem: ", value, data);
            var selectedType = self._selectizeType.getValue();
            self._problemForm.prefill({
                name: value,
                type: selectedType == 'optimizer' ? 'optimization' :
                    selectedType == 'clusterer' ? 'clustering' :
                    selectedType == 'classifier' ? 'classification' :
                    null
            });
            self._selectizeProblem.clear();
            self._selectizeProblem.removeOption(value);
            self._problemFormModal.show();
        }

    }

    self.onCreateProblem = function (problemData) {
        console.log("Problem created: ", problemData);
        var addTo = [];
        if (problemData.types.indexOf('optimization') > -1)
            addTo.push('optimizer')
        if (problemData.types.indexOf('clustering') > -1)
            addTo.push('clusterer')
        if (problemData.types.indexOf('classification') > -1)
            addTo.push('classifier')
        self._problemFormModal.hide();

        for (var i = 0; i < addTo.length; i++) {
            var type = addTo[i];
            self._problemsBySolverType[type].push(problemData);
            if (self._selectizeType.getValue() == type) {
                self._selectizeProblem.addOption({
                    text: problemData.name,
                    value: problemData._id
                });
                self._selectizeProblem.addItem(problemData._id)
            }
        };

    }

}
