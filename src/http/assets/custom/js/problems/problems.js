function ProblemItem ($listContainer, data) {
    var self = this;

    self._$listContainer = $listContainer
    self._template = '\
<tr><td class="clickable-list-item" data-problem-id="{{_id}}">{{name}}</td></tr>';
    self._data = data['name'];

    self._$item = $(render(self._template, data)).appendTo(self._$listContainer);

    self.get = function(attr) {
        return self._data[attr];
    }
}

function ProblemsList ($container) {
    var self = this;

    self._$container = $container;
    self._items = [];

    self.initialize = function () {
        self._items.length = 0;

        $.ajax({
            url: '/api/problems/list',
            dataType: 'json',
            success: function (results) {
                for (var i = 0; i < results.length; i++) {
                    self._items.push( new ProblemItem(
                        self._$container, results[i]));
                };
            },
            error: function (error) {
                console.error(error);
                $.UIkit.notify("An error occurred while retrieving the list of problems, see logs for details", {status:'danger'})
            }
        });
    }
}

function ProblemsCRUDPanel ($listContainer, $formContainer) {
    var self = this;

    self._$listContainer = $listContainer;
    self._$formContainer = $formContainer;

    self._problemList = new ProblemsList(self._$listContainer);
    self._problemForm = new ProblemForm(self._$formContainer);

    self.initialize = function () {
        self._problemList.initialize();
        self._problemForm.initialize();
    }
}
