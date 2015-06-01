/* Handles the log messages received on the websocket. */
function LogView($viewContainer) {
    var self = this;
    self._$viewContainer = $viewContainer;
    self._$logOutput = self._$viewContainer.find(".log-output");
    self._minDisplayLevel = 0;

    self.initialize = function (initMessage) {
        self._$logOutput.html(initMessage || '===== LOG SYSTEM STARTED =====');
        self._$logOutput.append('<br>');
    }

    self.onLogMessage = function (message, level) {
        var html = '<span class="log level-' + level + '"';
        if (level < self._minDisplayLevel)
            html += ' style="display: none"';
        html += '">'+ message + '</span>';
        self._$logOutput.append(html);
        if (level < self._minDisplayLevel)
            self._$logOutput.scrollTop(self._$logOutput[0].scrollHeight);
    }

    self.onSelectLevel = function (value) {
        value = parseInt(value);
        self._minDisplayLevel = value;
        self._$viewContainer.find('.log').css('display', '');
        for (var i = 0; i < value; i++) {
            self._$viewContainer.find('.log.level-' + i).css('display', 'none');
        };
    }

    self._$viewContainer.find("#select-level").selectize({
        onItemAdd: self.onSelectLevel
    });
    self._selectizeLevel = self._$viewContainer.find("#select-level")[0].selectize
    for (var i = 0; i <= 10; i++) {
        self._selectizeLevel.addOption({
            text: i == 0 ? "None" : "Level " + i,
            value: i
        });
        if (i == 0)
            self._selectizeLevel.addItem(0);
    };
}
