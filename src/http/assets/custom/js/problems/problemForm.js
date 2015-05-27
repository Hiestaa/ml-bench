var default_event = function () {
    console.log("Default event fired with arguments:", arguments);
}
/*
Instanciates an object able to manipulate the problem form.
* `$container`: jquery elements that contains the actual problem form
* `events`: (optional) an object containing events related to the form. This includes:
    * `saved`:function(problemData) fired when the a problem has been saved (either created or updated)
*/
function ProblemForm($container, events, options) {
    var self = this;

    self._$formContainer = $container;
    self._$form = $container.find('.problem-form');
    self._implementations = null;
    self._parameterTemplate = '\
<div class="uk-width-1-1 uk-width-medium-1-2 uk-width-large-1-3 parameter-field">\
    <label class="uk-form-label" for="input-{{name}}">{{name}}</label>\
    <input type="text" id="input-param-{{name}}" placeholder="{{name}}" class="uk-width-1-1" value="{{value}}">\
<div>\
';
    self._selectizeType = null;
    self._selectizeImplem = null;
    self._selectizeDataset = null;
    self._selectizeVisualization = null;
    self._currentProblem = null;

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

    /*
    The form can be initilized given a problem, in which case
    this problem will be displayed in the form, ready to be updated.
    * `options`: (optional) an object containing the following options:
        * `prefill`: an object containing association between a input name and value
          to pre-set the value
    */
    self.initialize = function (problem, options) {
        self._$form.find('#select-type').selectize({
            onItemAdd: self.onSelectType,
            onClear: self.onClearSelectType
        });
        self._$form.find('#select-implem').selectize({
            onItemAdd: self.onSelectImplem,
            onClear: self.onClearSelectImplem
        });
        self._$form.find('#select-dataset').selectize({});
        self._$form.find('#select-visualization').selectize({});
        self._selectizeType = self._$form.find('#select-type')[0].selectize;
        self._selectizeImplem = self._$form.find('#select-implem')[0].selectize;
        self._selectizeDataset = self._$form.find('#select-dataset')[0].selectize;
        self._selectizeVisualization = self._$form.find('#select-visualization')[0].selectize;
        self._$form.find('#clear').click(self.onClear);

        self._$form.find('#reset').click(self.onReset);
        self._$form.find('#submit').click(self.onSubmit);

        $.ajax({
            url: '/api/problems/implementations',
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
                if (problem)
                    self.setProblem(problem)
            },
            error: function (error) {
                console.error(error);
                $.UIkit.notify("An error occurred while retrieving the available implementations, see logs for details", {status:'danger'})
            }
        })
    }

    self.onSelectType = function (type) {
        self._selectizeImplem.clearOptions();
        self._selectizeImplem.clear();
        var added = false;
        for (var implem in self._implementations[type]) {
            if (implem === undefined)
                break;
            self._selectizeImplem.addOption({
                text: implem,
                value: implem
            });
            if (!added)
                self._selectizeImplem.addItem(implem);
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

    self.setProblem = function (problem) {
        console.log("Setting problem:", problem);
        self._selectizeType.clear();
        self._selectizeImplem.clear();
        self._selectizeDataset.clear();
        self._selectizeVisualization.clear();

        if (!self._implementations)
            return $.UIkit.notify("The existing implementations have not been loaded yet. Please try again later.", {status: 'danger'});
        // a problem may have more than one type. Select the first one
        // that is linked to the problem's implementation.
        var typeToDisplay = null;
        for (var type in self._implementations) {
            if (typeToDisplay !== null)
                break;
            if (problem.types.indexOf(type) > -1) {
                for (var implem in self._implementations[type]) {
                    if (problem.implementation == implem) {
                        typeToDisplay = type;
                        break;
                    }
                }
            }
        }
        if (typeToDisplay == null)
            return $.UIkit.notify("The problem's implementation does not exist anymore. You should delete and re-created it.", {status: 'danger'});
        // add the type and implementation of this problem to the selectize boxes
        self._selectizeType.addItem(typeToDisplay);
        self._selectizeImplem.addItem(implem);

        // fill in the name of the problem
        if (!problem._generatedName)
            self._$form.find('#input-name').val(problem.name);
        else
            self._$form.find('#input-name').val('');

        // fill in the parameters values
        for (var param_name in problem.parameters) {
            var input = self._$form.find('#input-param-' + param_name);
            if (input.length == 0)
                return $.UIkit.notify('The parameter named `' + param_name + "' does not exist for this implementation!", {status: 'danger'})
            input.val(problem.parameters[param_name]);
        }

        // save current problem to be able to reset the form.
        self._currentProblem = problem;
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
        console.log("Submitting form");
        var data = {}
        var classObj = null;

        if (!self.validate()) {
            return $.UIkit.notify('Some required fields have not be filled in. Please fill the fields marked in red then submit the form again.', {status: 'warning'});
        }

        data.name = self._$form.find('#input-name').val();
        data.implementation = self._selectizeImplem.getValue();
        data.dataset = self._selectizeDataset.getValue();
        data.visualization = self._selectizeVisualization.getValue();

        data.parameters = {}
        classObj = self._implementations[self._selectizeType.getValue()][data.implementation];
        for (var param_name in classObj.parameters) {
            data.parameters[param_name] = self._$form.find('#input-param-' + param_name).val();
        }
        data.parameters = JSON.stringify(data.parameters);

        if (self._currentProblem !== null)
            data._id = self._currentProblem._id;

        $.ajax({
            url: '/api/problems/save',
            type: 'post',
            dataType: 'json',
            data: data,
            success: function (data) {
                $.UIkit.notify('The problem ' + data.name + ' has successfully been saved!');
                self._currentProblem = null;
                self.onReset();
                self._events.saved(data);
            },
            error: function (error) {
                console.error(error);
                $.UIkit.notify("An error occurred while saving the problem: " + data.name, {status: 'danger'});
            }
        })
    }

    self.onReset = function () {
        console.log("Resetting form");
        if (self._currentProblem)
            return self.setProblem(self._currentProblem);
        // clear items only, not options
        self._selectizeType.clear();
        self._selectizeImplem.clear();
        self._selectizeDataset.clear();
        self._selectizeVisualization.clear();
        self._$form.find('#input-name').val('');
        self._$form.find('#description').html('Select an implementation to view its description here...');
        self._$form.find('#parameters').html('');
        self._$form.find('#input-name').removeClass('invalid');
        self._selectizeType.$control.removeClass('invalid');
        self._selectizeImplem.$control.removeClass('invalid');
    }

    self.onClear = function () {
        self._currentProblem = null;
        self.onReset();
    }

}
