function ExpandablePanel($panelContainer) {
    var self = this;

    self._$panelContainer = $panelContainer;

    self._$panelContainer.find('#full-screen-icon').remove();
    self._$expandIcon = $('<a href="#" class="uk-icon-button uk-icon-expand" id="full-screen-icon"></i>')
        .appendTo(self._$panelContainer);

    self.onClickExpand = function () {
        console.log("Expand!");
        self._$panelContainer.addClass('expanded');
        self._$expandIcon.off().click(self.onClickCompress)
            .addClass("uk-icon-compress").removeClass('uk-icon-expand');
        self.onExpand();
    }


    self.onClickCompress = function () {
        console.log("Compress");
        self._$panelContainer.removeClass('expanded');
        self._$expandIcon.off().click(self.onClickExpand)
            .addClass("uk-icon-expand").removeClass('uk-icon-compress');
        self.onCompress();
    }

    self._$expandIcon.off().click(self.onClickExpand);
}


ExpandablePanel.prototype.onExpand = function () {
    console.log("Default onExpand");
    // override this function to execute some code when the window is expanded
}
ExpandablePanel.prototype.onCompress = function () {
    console.log("Default onCompress");
    // override this function to execute some code when the window is compressed
}
