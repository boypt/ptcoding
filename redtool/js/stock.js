$(function() {
    var cur_pfid = localStorage.getItem('cur_pfid');
    resumenums();
    show_data_table(cur_pfid);

    $('#sharenums').blur(function () {savenums();});
    $('#is_fund').click(function () {
        $("#data_table_tb"+CURPFID).DataTable().destroy(true);
        savenums();
    });

});

function stoset(key, obj) { localStorage.setItem(key, JSON.stringify(obj)); }
function stoget(key) {
    var dt = localStorage.getItem(key);
    if (dt !== null) {
        return JSON.parse(dt);
    }else{
        return null;
    }
}

function savenums(pfid) {
    if(pfid===undefined)
        pfid = CURPFID;
    var ids = $.trim($('#sharenums').val());
    var is_fund = $("#is_fund").prop('checked');
    stoset("profile_data"+pfid, {"ids":ids, "is_fund":is_fund});
};


function resumenums () {
    var cur_pfid = localStorage.getItem('cur_pfid');
    if(cur_pfid === null) {
        cur_pfid = '1';
        localStorage.setItem('cur_pfid',cur_pfid);
    }
    window.CURPFID = cur_pfid;

    $(".profile_btn[data-pfid="+cur_pfid+"]").addClass('button-primary')
    var dt = stoget("profile_data"+cur_pfid);

    $('#sharenums').val('');
    if(dt!==null) {
        $('#sharenums').val(dt.ids);
        $("#is_fund").prop("checked", dt.is_fund);
    } else {
        savenums(cur_pfid);
    }
}



function parsenums (pfid) {

    if(pfid===undefined) {
        pfid = CURPFID;
    }

    var dt = stoget("profile_data"+pfid);

    if(dt===null || dt.ids.length===0) { return []; }

    if(dt.is_fund) {
        var qs = $.map(dt.ids.match(/[0-9]{6}/g), function(v) { return 'f_'+v; });
    }else{
        var qs = $.map(dt.ids.match(/[0-9]{6}/g), function(v) {
            var marketsig = parseInt(v.substr(0,1));
            var pfx = marketsig>=5?'s_sh':'s_sz';
            return pfx+v;
        });
    }

    return qs;
}


function init_data_table(tbid, dt) {

    if(!$(tbid).length) {
        $("<table>").attr("id", tbid.substr(1)).addClass("compact").appendTo("#data_table_div");
    }

    if(!$.fn.dataTable.isDataTable(tbid)) {

        if(dt.is_fund) {
            var colms = [
                { "title": "名称", "className":"dt-nowrap",
                    "render": function ( data, type, row ) { 
                        return '<a data-code="'+row[row.length-1]+'" class="val_target" href="#">'+data+'</a>'; },},
                { "title": "净值" },
                { "title": "累计净值" },
                { "title": "昨净" },
                { "title": "净值日期" },
                { "title": "？？", "visible": false },
                { "title": "涨跌幅", 
                    "data": function ( row, type, val, meta ) {
                        var val = parseFloat(row[1]);
                        var lastval = parseFloat(row[3]);
                        return ((val-lastval)/lastval*100).toFixed(2)+'%';
                    } 
                }
            ];

        } else {
            var colms = [
                { "title": "名称", "className":"dt-nowrap",
                    "render": function ( data, type, row ) { 
                        return '<a data-code="'+row[row.length-1]+'" class="val_target" href="#">'+data+'</a>'; },},
                { "title": "现价" },
                { "title": "涨跌" },
                { "title": "涨跌幅",
                    "render": function ( data, type, row ) { return data+'%'; },
                },
                { "title": "现量", "visible": false },
                { "title": "现手", "visible": false }
            ];
        }


        $(tbid).dataTable( {
            "paging":   false,
            "ordering": false,
            "info":     false,
            "searching":false,
            "deferRender": true,
            "columns": colms,
            "drawCallback": function( settings ) {
                var tb = this.api();
                tb.rows().every( function () {
                    var row = this.data();
                    var incr = 0;
                    if(dt.is_fund) { incr = parseFloat(row[1]) - parseFloat(row[3]);; }
                    else { incr = parseFloat(row[2]); }

                    if(incr > 0) { $(this.node()).addClass('reddata'); }
                    else if (incr < 0) { $(this.node()).addClass('greendata'); }
                });
            }
        });
    }
}

function show_data_table(pfid) {

    var tbid = "#data_table_tb"+pfid;
    var dt = stoget("profile_data"+pfid);

    if(dt===null || dt.ids.length === 0)
        return false;

    if(!$.fn.dataTable.isDataTable(tbid)) {
        init_data_table(tbid, dt);
    }

    var tb = $(tbid).DataTable();
    var dataSet = $.map(parsenums(), function (v) {
        var val = localStorage.getItem(v);
        if(val !== null) {
            var r = val.split(',');
            r.push(v);
            return [r];
        }
    });

    tb.clear().rows.add(dataSet).draw();
}

$(function () {

    $('#update_share').click(function(evn) {
        $("#msgbar").text('Loading ...').slideDown();
        var qs = parsenums();

        if(qs.length > 0) {
            var qsstr = 'list='+qs.join(',');
            $.getScript('api.php?'+qsstr, function () {
                $.each(qs, function (i,v) {
                    localStorage.setItem(v, window['hq_str_'+v]);
                });
                show_data_table(CURPFID);
                $("#msgbar").slideUp();
            });
        }
        return false;
    });

    $(".profile_btn").click(function(evn) {
        var btn = $(evn.target)
        var pfid = btn.data("pfid");
        var lo_cur_pfid = parseInt(localStorage.getItem('cur_pfid'));

        if (lo_cur_pfid !== pfid) {
            $(".profile_btn").removeClass('button-primary');
            btn.addClass('button-primary');

            localStorage.setItem('cur_pfid', pfid);
            resumenums();

            $("#data_table_div .dataTables_wrapper").fadeOut(400, function(){
                show_data_table(pfid);
            });
            $("#data_table_tb"+pfid).parent(".dataTables_wrapper").fadeIn();
        }

        return false;

    });

    $("#show_neat_value").click(function() {
        var tb = $("#data_table_tb"+CURPFID).DataTable();
        var dt = tb.column(1).data();
        var netv = $("#neat_val").empty().text(dt.join('\n'));
        $("#neat_val_window").modal({
            opacity:80,
            overlayCss: {backgroundColor:"#333"},
            minHeight:400,
            minWidth: 100,
        });

    });

    $("#data_table_div").on('click', 'a.val_target', function(evn) {
        var elm = $(evn.target);
        var code = elm.data('code');
        if(code.substr(0,2) == "f_") {
            code = code.match(/[0-9]{6}$/)[0];
            var url = 'http://fund.eastmoney.com/'+code+'.html';
        }else if(code.substr(0,2) == "s_") {
            code = code.substr(2);
            var url = 'http://quote.eastmoney.com/'+code+'.html';
        }
        window.open(url, '_blank');
        return false;
    });
});

