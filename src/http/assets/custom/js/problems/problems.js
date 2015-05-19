
var default_event = function () {
    console.log("Default event fired with arguments:", arguments);
}
/*
Creates a new problem item and appends it the the given list container.
* `$listContainer`: jquery elements to which problem items should be appended
* `data`: data related to this problem, expected to contain all the fields described in the problem service.
* `events`: (optional) an object containing events that can be listened on this problem item. This includes:
    * `click`:function(problemData) fired when the problem item is clicked.
*/
function ProblemItem ($listContainer, data, events) {
    var self = this;

    self._$listContainer = $listContainer
    self._template = '\
<tr><td class="clickable-list-item" data-problem-id="{{_id}}">{{name}}</td></tr>';
    self._data = data;

    self._$item = $(render(self._template, data)).appendTo(self._$listContainer);

    if (!events)
        events = {}
    self._events = {
        click: events.click || default_event
    }

    self._$item.click(function () {
        self._events.click(self._data);
    })
}

/*
Creates a new problem list in the given container.
The problem list will fetch all exsting problems when initialized.
* `$container`: the jquery element container in which to display the list
* `events`: (optional) an object containing events that can be listened on this problem list. This includes:
    * `problemClick`:function(problemData) fired when a problem is clicked
*/
function ProblemsList ($container, events) {
    var self = this;

    self._$container = $container;
    self._items = [];

    if (!events)
        events = {}
    self._events = {
        problemClick: events.problemClick || default_event
    }

    self.initialize = function () {
        self._items.length = 0;
        self._$container.html('');

        $.ajax({
            url: '/api/problems/list',
            dataType: 'json',
            success: function (results) {
                for (var i = 0; i < results.length; i++) {
                    self._items.push( new ProblemItem(
                        self._$container, results[i], {
                            click: self._events.problemClick
                        }));
                };
            },
            error: function (error) {
                console.error(error);
                $.UIkit.notify("An error occurred while retrieving the list of problems, see logs for details", {status:'danger'})
            }
        });
    }
}

/*
Creates the panel able to perform CRUD operations on the problems collection.
* `$listContainer` is the jquery element in which the list of problems will be displayed
* `$formContainer` is the jquery element in which the problem form can be found
*/
function ProblemsCRUDPanel ($listContainer, $formContainer) {
    var self = this;

    self._$listContainer = $listContainer;
    self._$formContainer = $formContainer;

    self.initialize = function () {
        self._problemList.initialize();
        self._problemForm.initialize();
    }

    self.onProblemClick = function (problemData) {
        self._problemForm.setProblem(problemData);
    }
    self.onProblemSaved = function (problemData) {
        self._problemList.initialize();
    }

    self._problemList = new ProblemsList(self._$listContainer, {
        problemClick: self.onProblemClick
    });
    self._problemForm = new ProblemForm(self._$formContainer, {
        saved: self.onProblemSaved
    });
}
