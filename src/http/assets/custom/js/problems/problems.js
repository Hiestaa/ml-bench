
var default_event = function () {
    console.log("Default event fired with arguments:", arguments);
}
/*
Creates a new problem item and appends it the the given list container.
* `$listContainer`: jquery elements to which problem items should be appended
* `data`: data related to this problem, expected to contain all the fields described in the problem service.
* `events`: (optional) an object containing events that can be listened on this problem item. This includes:
    * `click`:function(problemData) fired when the problem item is clicked.
    * `del`:function(problemData) fired when the problem item is deleted.
*/
function ProblemItem ($listContainer, data, events) {
    var self = this;

    self._$listContainer = $listContainer
    self._template = '\
<tr><td class="clickable-list-item" data-problem-id="{{_id}}" id="{{id}}">\
    {{name}}\
    <button class="uk-button uk-button-danger uk-button-small remove-item"><i class="uk-icon-minus-circle"></i></button>\
</td></tr>';
    self._data = data;

    self._$item = $(render(self._template, data)).appendTo(self._$listContainer);

    if (!events)
        events = {}
    self._events = {
        click: events.click || default_event,
        del: events.del || default_event
    }

    self._$item.find('.remove-item').mouseover(function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        return false;
    })
    self._$item.find('.remove-item').click(function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        self._events.del(self._data)
        return false;
    })
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
    * `problemDel`:function(problemData) fired when a problem is removed
*/
function ProblemsList ($container, events) {
    var self = this;

    self._$container = $container;
    self._items = [];

    if (!events)
        events = {}
    self._events = {
        problemClick: events.problemClick || default_event,
        problemDel: events.problemDel || default_event
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
                            click: self._events.problemClick,
                            del: self._events.problemDel
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
        self._$listContainer.find('.clickable-list-item').removeClass('active');
        self._$listContainer.find('#' + problemData._id).addClass('active');
        self._problemForm.setProblem(problemData);
    }
    self.onProblemDelete = function (problemData) {
        $.ajax({
            url: '/api/problems/byId',
            type: 'delete',
            dataType: 'json',
            data: {
                _id: problemData._id
            },
            success: function () {
                self._problemForm.onClear();
                self._problemList.initialize();
            },
            error: function () {
                $.UIkit.notify("An error occurred while deleting this problem. See logs for details.");
            }
        })
    }
    self.onProblemSaved = function (problemData) {
        self._problemList.initialize();
    }

    self._problemList = new ProblemsList(self._$listContainer, {
        problemClick: self.onProblemClick,
        problemDel: self.onProblemDelete
    });
    self._problemForm = new ProblemForm(self._$formContainer, {
        saved: self.onProblemSaved
    });
}
