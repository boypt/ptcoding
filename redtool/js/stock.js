/* ---------------------------------  Portfolio -----------------------------------------------------*/
var Portfolio = function (pfid)  {
    this.pfid = pfid;
    this.storage_key = "profile_data"+this.pfid;
    this.table_id = "#data_table_tb"+this.pfid;
    this.table_api = null;
    this.is_fund = true;
    this.ids = '';
    this.sina_ids = [];
    this.last_update = null;
    this.values = {};
    this.button =  $('<button class="profile_btn pure-button">').attr("id", "_pfbtn"+pfid).attr("data-pfid", pfid).text("组合"+pfid);
    this.button_wrap = $('<li class="pure-menu-item">').append(this.button).appendTo("#profile_nav");
    this.restore();
    if (pfid == CURPFID) {
        this.button.addClass("pure-button-active");
    }
}

Portfolio.prototype.save = function () {
    var vals = {
        "is_fund":this.is_fund,
        "ids":this.ids,
        "sina_ids":this.sina_ids,
        "values":this.values,
        "last_update":this.last_update
    }
    localStorage.setItem(this.storage_key, JSON.stringify(vals)); 
}

Portfolio.prototype.restore = function () {
    var dt = localStorage.getItem(this.storage_key);
    if (dt != null) {
        var vals = JSON.parse(dt);
        $.extend(this, vals);
    }
}

Portfolio.prototype.remove_data = function () {
    localStorage.removeItem(this.storage_key);
}

Portfolio.prototype.sync_from_dom = function () {
    var ids = $.trim($('#sharenums').val());
    var is_fund = $("#is_fund").prop('checked');
    if(is_fund != this.is_fund) {
        this.destroy_table();
    }
    this.ids = ids;
    this.is_fund = is_fund;
    this.parse_ids();
    this.save();
}

Portfolio.prototype.sync_to_dom = function () {
    $('#sharenums').val(this.ids);
    $("#is_fund").prop("checked", this.is_fund);
}

Portfolio.prototype.parse_ids = function () {

    var qs = [];

    if (this.ids.length > 0) {
        if(this.is_fund) {
            qs = $.map(this.ids.match(/[0-9]{6}/g), function(v) { return 'f_'+v; });
        }else{
            qs = $.map(this.ids.match(/[0-9]{6}/g), function(v) {
                var marketsig = parseInt(v.substr(0,1));
                var pfx = marketsig>=5?'s_sh':'s_sz';
                return pfx+v;
            });
        }
    }

    this.sina_ids = qs;
    return qs;
}

Portfolio.prototype.init_data_table = function () {

    var tbid = this.table_id;

    if(!$(tbid).length) {
        $("<table>").attr("id", tbid.substr(1)).appendTo("#data_table_div");
    }

    var colms, drawcb;

    var val_render = function ( data, type, row ) {
        var cls = data.substr(0,1) === '-' ? "price negtive":"price";
        return '<span class="'+cls+'">'+data+'</span>';
    }

    if(!$.fn.dataTable.isDataTable(tbid) && this.table_api === null) {

        if(this.is_fund) {
            colms = [
                { "title": "名称",
                    "className":"dt-nowrap tg_name",
                    "orderable": false,
                    "render": function ( data, type, row ) { 
                        var code = row[row.length-1].substr(2);
                        return '<a target="_blank" href="http://fund.eastmoney.com/'+code+'.html">'+data+'</a>'; },},
                { "title": "净值",
                    "render": val_render,
                },
                { "title": "累计净值",
                    "render": val_render,
                },
                { "title": "昨净",
                    "render": val_render,
                },
                { "title": "净值日期", "orderable": false,
                },
                { "title": "？？", "visible": false },
                { "title": "涨跌幅", 
                    "data": function ( row, type, val, meta ) {
                        var val = parseFloat(row[1]);
                        var lastval = parseFloat(row[3]);
                        return ((val-lastval)/lastval*100).toFixed(2)+'%';
                    },
                    "render": val_render,
                }
            ];

            drawcb = function( settings ) {
                var tb = this.api();
                tb.rows().every( function () {
                    var row = this.data();
                    var incr = parseFloat(row[1]) - parseFloat(row[3]);
                    if(incr > 0) { $(this.node()).addClass('reddata'); }
                    else if (incr < 0) { $(this.node()).addClass('greendata'); }
                });
            }


        } else {
            colms = [
                { "title": "名称",
                    "className":"dt-nowrap tg_name",
                    "orderable": false,
                    "render": function ( data, type, row ) {
                        var code = row[row.length-1].substr(2);
                        return '<a target="_blank" href="http://quote.eastmoney.com/'+code+'.html">'+data+'</a>'; },},
                { "title": "现价",
                    "render": val_render,
                },
                { "title": "涨跌",
                    "render": val_render,
                },
                { "title": "涨跌幅",
                    "render": function (d,t,r){return val_render(d+'%',t,r);},
                },
                { "title": "现量", "visible": false },
                { "title": "现手", "visible": false }
            ];

            drawcb = function( settings ) {
                var tb = this.api();
                tb.rows().every( function () {
                    var row = this.data();
                    var incr = parseFloat(row[2]);
                    if(incr > 0) { $(this.node()).addClass('reddata'); }
                    else if (incr < 0) { $(this.node()).addClass('greendata'); }
                });
            }
        }

        var tb = $(tbid).dataTable( {
            "paging":   false,
            "ordering": true,
            "order":    [],
            "info":     false,
            "searching":false,
            "deferRender": true,
            "columns": colms,
            "drawCallback":drawcb
        });

        this.table_api = tb.api();
    }
}

Portfolio.prototype.show_data_table = function () {
    $("#last_update").text(this.last_update);

    var _this = this;
    var dataSet = $.map(this.sina_ids, function (v) {
        var val = _this.values[v];
        if(val) {
            var r = val.split(',');
            r.push(v);
            return [r];
        }
    });

    this.init_data_table();
    this.table_api.clear().rows.add(dataSet).draw();
    $(this.table_id).parent(".dataTables_wrapper").slideDown();
}

Portfolio.prototype.update_data = function (callback) {
    var qs = this.parse_ids();

    if(qs.length > 0) {
        $("#msgbar").text('Updating ...').slideDown();
        console.log("update pfid " + this.pfid);
        var qsstr = 'list='+qs.join(',');
        var _this = this;
        $.getScript('api.php?'+qsstr, function () {
            $.each(qs, function (i,v) {
                _this.values[v] = window['hq_str_'+v];
            });
            _this.last_update = new Date().toLocaleString();
            _this.save();

            if(typeof callback === 'function') {
                callback(_this);
            }
        });
    }

    return qs.length;
}

Portfolio.prototype.show_neat_value = function () {
    if(this.table_api === null)
        return;
    var dt = this.table_api.column(1).data();
    var netv = $("#neat_val").empty().text(dt.join('\n'));
    $("#neat_val_window").modal({
        opacity:80,
        overlayCss: {backgroundColor:"#333"},
        minHeight:400,
        minWidth: 100,
        overlayClose: true,
        onShow: function () {
            var _v = $('#neat_val');
            _v.outerHeight(0);
            _v.outerHeight(_v.get(0).scrollHeight);
        }
    });
}

Portfolio.prototype.destroy_table = function () {
    this.table_api.destroy(true);
    this.table_api = null;
}

Portfolio.prototype.destroy_button = function () {
    $("#_pfbtn"+this.pfid).remove();
}

Portfolio.prototype.activate = function () {
    this.sync_to_dom();
    this.init_data_table();
    this.show_data_table();
    if(!this.button.hasClass("pure-button-active")) {
        this.button.addClass("pure-button-active")
    }
}

Portfolio.prototype.deactivate = function () {
    $(this.table_id).parent(".dataTables_wrapper").slideUp();
    this.button.removeClass("pure-button-active");
}

/* --------------------------------------------------------------------------------------------------------*/

/* ---------------------------------  PortfolioIdList -----------------------------------------------------*/

var PortfolioIdList = function ()  {
    this.storage_key = "pf_list";
    this.list = ["1"];
    window.CURPFID = localStorage.getItem('cur_pfid') || "1";
    this.restore();
}

PortfolioIdList.prototype.save = function () {
    localStorage.setItem(this.storage_key, JSON.stringify(this.list)); 
}

PortfolioIdList.prototype.restore = function () {
    var dt = localStorage.getItem(this.storage_key);
    if (dt != null) {
        this.list = JSON.parse(dt);
    }
}

PortfolioIdList.prototype.add = function () {
    var last = $(".profile_btn:last").attr("data-pfid");
    var _newpf = (parseInt(last)+1).toString();
    this.list.push(_newpf);
    this.save();
    return _newpf;
}

PortfolioIdList.prototype.remove = function (pfid) {
    this.list = this.list.filter(function(x) { return x !== pfid;});
    this.save();
}

PortfolioIdList.prototype.build_portfolios = function (pfos) {
    $.each(this.list, function(i,v) {
        var _o = new Portfolio(v);
        pfos[v] = _o;
    });
}
/* --------------------------------------------------------------------------------------------------------*/

/* ------------------------------------jQuery Event Handlings----------------------------------------------*/

var _reg_event_handlers = function () {

    $("#msgbar").text("Initiating ... Registering Handlers ...");

    /* ----- NAV Buttons ------- */
    $('#redraw').click(function(evn) {
        var o = _Portfolio[CURPFID];
        o.destroy_table();
        o.show_data_table();
        return false;
    });

    $('#update_share').click(function(evn) {
        var cnt = 0;
        $.each(_Portfolio, function () {
            var len = this.update_data(function (pfo) {
                if(pfo.pfid === CURPFID) {
                    console.log("refresh pfid" + pfo.pfid);
                    pfo.show_data_table();
                }
                console.log("cnt out "+cnt);
                if(--cnt === 0) {
                    $("#msgbar").slideUp();
                }
            });
            if (len > 0) cnt++;
            console.log("cnt in "+cnt);
        });
        return false;
    });

    $("#show_neat_value").click(function() {
        var o = _Portfolio[CURPFID];
        o.show_neat_value();
        return false;
    });

    $("#clear_current").click(function () {
        var r = confirm("Confirm");
        if (r === true) {
            var o = _Portfolio[CURPFID];
            o.destroy_table();
            o.destroy_button();
            o.remove_data();
            _List.remove(CURPFID);
            var _oldpfid = CURPFID;
            $(".profile_btn:last").trigger('click');
            delete _Portfolio[ _oldpfid ];
        }
        return false;
    });
    /*----------------------------------------*/

    /* ----------- Profile Button ------------*/
    $("#profile_nav").on("click", "button.profile_btn", function(evn) {
        var pfid = $(evn.target).attr("data-pfid");

        // switch
        if (typeof(CURPFID) !== "undefined" && CURPFID !== pfid) {
            _Portfolio[CURPFID].deactivate();
            CURPFID = pfid;
            localStorage.setItem('cur_pfid', pfid);
            _Portfolio[pfid].activate();
        }

        return false;
    });

    $("#btn_add_profile").click(function () {
        var key = _List.add();
        var _o = new Portfolio(key);
        window._Portfolio[key] = _o;
        return false;
    });
    /*----------------------------------------*/

    /*--------------Input Controls -----------*/
    $('#sharenums').blur(function () {
        var o = _Portfolio[CURPFID];
        o.sync_from_dom();
        o.save();
    });
    $('#is_fund').click(function () {
        var o = _Portfolio[CURPFID];
        o.sync_from_dom();
        o.save();
    });
    $('#neat_val').mouseover(function () {
        $(this).select();
    });
    /*----------------------------------------*/
}

var _ui_init = function () {
    $("#msgbar").text("Building UI Components ...");
    window._List = new PortfolioIdList();
    window._Portfolio = {};
    _List.build_portfolios(window._Portfolio);
}

