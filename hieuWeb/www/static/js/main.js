function changyan_login() {
    $("#login-modal").modal("toggle");
}
$(document).ready(function () {
    if (typeof String.prototype.trim !== 'function') {
        String.prototype.trim = function () {
            return this.replace(/^\s+|\s+$/g, '');
        }
    }
    OJ.Widget.InitWidget();
    
    $.getJSON("http://hieu.myexample.cc/user/acratio/", function(data) {
        Highcharts.chart('active-degree', {
            title: {
                text: ''
            },
            yAxis: {
                tickInterval: 50,
                min: 0,
                max: 100,
                title: {
                    text: '通过率'
                }
            },
            xAxis: {
                tickWidth: 0,
                labels: {
                    enabled: false
                }
            },
            legend: {
                enabled: false,
            },
            credits: {
                enabled: false,
            },
            exporting: {
                enabled: false
            },
            series: [{
                name: '通过率',
                data: data
            }],
            tooltip: {
                pointFormat: '<span style="color:{point.color}">\u25CF</span> {series.name}: <b>{point.y}%</b><br/>'
            }
        });
    });
    
    $(".btn-register").click(function () {
        $("#login-modal").modal("toggle");
        $("#progress-modal").modal("toggle");
    });

    var refresh_user_regisert_captcha = function () {
        $("#register-captcha img").attr("src", $("#register-captcha img").attr("data-src") + "?" + (new Date()).getTime());
    };

    var refresh_user_login_captcha = function () {
        $("#login-captcha img").attr("src", $("#login-captcha img").attr("data-src") + "?" + (new Date()).getTime());
    };

    $("#register-captcha img").click(function () {
        refresh_user_regisert_captcha();
    });

    $("#login-captcha img").click(function () {
        refresh_user_login_captcha();
    });

    $("#user-register input").focus(function () {
        $(this).parent().removeClass();
        $(this).parent().addClass("form-group");
        $(this).siblings(".help-block").text("");
        if ($(this).attr("name") == "captcha" && $("#register-captcha").css("display") == "none") {
            $("#register-captcha").css("display", "block");
            refresh_user_regisert_captcha();
        }
    });

    $("#user-login input").focus(function () {
        $(this).parent().removeClass();
        $(this).parent().addClass("form-group");
        $(this).siblings(".help-block").text("");
        if ($(this).attr("name") == "captcha" && $("#login-captcha").css("display") == "none") {
            $("#login-captcha").css("display", "block");
            refresh_user_login_captcha();
        }
    });

    $("#user-register").submit(function (e) {
        e.preventDefault();
        $("#user-register button[type='submit']").attr("disabled", true);
        var data = {};
        $.each($(this).serializeArray(), function () {
            data[this.name] = this.value.trim();
        });

        // 重置错误提示
        $("#user-register input").each(function () {
            $(this).parent().removeClass();
            $(this).parent().addClass("form-group");
            $(this).siblings(".help-block").text("");
        });

        // 发送注册数据
        OJ.User.Post($(this).attr('action'), data, function (data) {
            $("#user-register button[type='submit']").removeAttr("disabled");
            if (data.status == "success") {
                window.location.reload();
            }
            if (data.status == "error") {
                if (data.errors.account != undefined) {
                    $("#user-register").find("input[name='account']").parent().addClass("has-warning");
                    $("#user-register").find("input[name='account']").siblings(".help-block").text(data.errors.account);
                }
                if (data.errors.password != undefined) {
                    $("#user-register").find("input[name='password']").parent().addClass("has-warning");
                    $("#user-register").find("input[name='password']").siblings(".help-block").text(data.errors.password);
                }
                if (data.errors.captcha != undefined) {
                    $("#user-register").find("input[name='captcha']").parent().addClass("has-warning");
                    $("#user-register").find("input[name='captcha']").siblings(".help-block").text(data.errors.captcha);
                }
            }
        });
        refresh_user_regisert_captcha();
        return false;
    });

    $("#user-login").submit(function (e) {
        e.preventDefault();
        $("#user-login button[type='submit']").attr("disabled", true);
        var data = {};
        $.each($(this).serializeArray(), function () {
            data[this.name] = this.value.trim();
        });

        // 重置错误提示
        $("#user-login input").each(function () {
            $(this).parent().removeClass();
            $(this).parent().addClass("form-group");
            $(this).siblings(".help-block").text("");
        });

        // 发送登录数据
        OJ.User.Post($(this).attr('action'), data, function (data) {
            $("#user-login button[type='submit']").removeAttr("disabled");
            if (data.status == "success") {
                window.location.reload();
            }
            if (data.status == "error") {
                if (data.errors.account != undefined) {
                    $("#user-login").find("input[name='account']").parent().addClass("has-warning");
                    $("#user-login").find("input[name='account']").siblings(".help-block").text(data.errors.account);
                }
                if (data.errors.password != undefined) {
                    $("#user-login").find("input[name='password']").parent().addClass("has-warning");
                    $("#user-login").find("input[name='password']").siblings(".help-block").text(data.errors.password);
                }
                if (data.errors.captcha != undefined) {
                    $("#user-login").find("input[name='captcha']").parent().addClass("has-warning");
                    $("#user-login").find("input[name='captcha']").siblings(".help-block").text(data.errors.captcha);
                }
            }
        });
        refresh_user_login_captcha();
        return false;
    });

    $("#submit-solution [name]").focus(function () {
        $(this).parent().removeClass();
        $(this).parent().addClass("form-group");
        $(this).siblings(".help-block").text("");
    });

    $("#submit-solution [name]").each(function () {
       $(this).val('');
    });

    $("#submit-solution").submit(function (e) {
        e.preventDefault();
        $("#submit-solution button[type='submit']").attr("disabled", true);
        var data = {};
        $.each($(this).serializeArray(), function () {
            data[this.name] = this.value.trim();
        });

        // 重置错误提示
        $("#submit-solution .form-group").each(function () {
            $(this).parent().removeClass();
            $(this).parent().addClass("form-group");
        });
        $("#submit-solution .form-group .help-block").each(function () {
            $(this).text("");
        });

        // 提交解答
        OJ.User.Post($(this).attr('action'), data, function (data) {
            $("#submit-solution button[type='submit']").removeAttr("disabled");
            if (data.status == "unlogin") {
                $("#login-modal").modal('show');
            }
            if (data.status == "success") {
                alert('提交成功');
                window.location.reload();
            }
            if (data.status == "error") {
                if(data.error_msg != undefined) {
                    alert(data.error_msg);
                    return;
                }
                if (data.errors.code != undefined) {
                    $("#submit-solution").find(" [name='code']").parent().addClass("has-warning");
                    $("#submit-solution").find(" [name='code']").siblings(".help-block").text(data.errors.code);
                }
                if (data.errors.lang != undefined) {
                    $("#submit-solution").find(" [name='lang']").parent().addClass("has-warning");
                    $("#submit-solution").find(" [name='lang']").siblings(".help-block").text(data.errors.lang);
                }
            }
        });
        return false;
    });
    
});