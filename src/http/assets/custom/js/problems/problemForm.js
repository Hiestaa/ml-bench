function ProblemForm($container, events) {
    var self = this;

    self._$formContainer = $container;
    self._$form = $container.find('.problem-form');
    self._implementations = null;
    self._parameterTemplate = '\
<div class="uk-width-1-1 uk-width-medium-1-2 uk-width-large-1-3 parameter-field">\
    <label class="uk-form-label" for="select-{{name}}">{{name}}</label>\
    <input type="text" placeholder="{{name}}" class="uk-width-1-1">\
<div>\
'

    /*
    The form can be initilized given a problem, in which case
    this problem will be displayed in the form, ready to be updated.
    */
    self.initialize = function (problem) {
        self._$form.find('#select-type').selectize({
            onItemAdd: self.onSelectType
        });
        self._$form.find('#select-implem').selectize({
            onItemAdd: self.onSelectImplem
        });
        self._selectizeType = self._$form.find('#select-type')[0].selectize;
        self._selectizeImplem = self._$form.find('#select-implem')[0].selectize;

        $.ajax({
            url: '/api/problems/implementations',
            dataType: 'json',
            success: function (results) {
                self._implementations = results;
                self._selectizeType.clearOptions();
                var added = false;
                for (var type in self._implementations) {
                    self._selectizeType.addOption({
                        value: type,
                        text: type
                    });
                    if (!added) {
                        self._selectizeType.addItem(type);
                        added = true;
                    }
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
        self._$form.find('#description').html('')
        self._$form.find('#parameters').html('')
        if (!implem) {
            return;
        }
        selectedType = self._selectizeType.getValue();
        classObj = self._implementations[selectedType][implem];
        self._$form.find('#description').html(
            formatDoc(classObj.description));
        for (var i = 0; i < classObj.parameters.length; i++) {
            self._$form.find('#parameters').append(
                render(self._parameterTemplate, {name: classObj.parameters[i]}));
        };
    }

    self.setProblem = function (problem) {
        console.log("Setting problem:", problem);
    }

    self.onSubmit = function () {
        console.log("Submitting form");
    }

    self.onReset = function () {
        console.log("Resetting form");
    }

}
