var OJ = (function () {
    return {
        User: {
            Path: "",
            SetPath: function (path) {
                this.Path = path;
            },
            Post: function (url, data, callback) {
                var _this = this;
                $.post(_this.Path + url, data, callback);
            },
        },
        Widget: {
            Path: "",
            SetPath: function (path) {
                this.Path = path;
            },
            Ajax: function (url, container) {
                var _this = this;
                $.get(url, function (data, status) {
                    var element = $(data);
                    $(container).html(element);
                    element.find(".widget-refresh").click(function (event) {
                        _this.Ajax(url, container);
                    });
                });
            },
            SystemInfo: function (container) {
                var _this = this;
                $(container).each(function (idx, value) {
                    _this.Ajax(_this.Path + "/widget/system_info/", value);
                });
            },
            MyContest: function (container) {
                var _this = this;
                $(container).each(function (idx, value) {
                    _this.Ajax(_this.Path + "/widget/my_contest/", value);
                });
            },
            MySubmit: function (container) {
                var _this = this;
                $(container).each(function (idx, value) {
                    _this.Ajax(_this.Path + "/widget/my_submit/", value);
                });
            },
            InitWidget: function () {
                this.SystemInfo("[id*='system-info']");
                this.MyContest("[id*='my-contest']");
                this.MySubmit("[id*='my-submit']");
            }
        },
    }
}());