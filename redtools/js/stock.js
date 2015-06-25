$(function() {
    resumenums();
    updatetable();
    $('#sharenums').blur(savenums);
    $('#is_fund').click(savenums);
});

function resumenums () {
    var cur_pfid = localStorage.getItem('cur_pfid');
    if(cur_pfid === null) {
        cur_pfid = '1';
        localStorage.setItem('cur_pfid',cur_pfid);
    }

    $(".profile_btn[data-pfid="+cur_pfid+"]").addClass('button-primary')

    var ids = localStorage.getItem('sharenums_'+cur_pfid);
    var is_fund = localStorage.getItem('is_fund_'+cur_pfid);

    $('#sharenums').val('');
    if(ids !== null && is_fund !== null) {
        $('#sharenums').val(ids);
        $("#is_fund").prop("checked", is_fund==1);
    }
}

function savenums () {
    var cur_pfid = localStorage.getItem('cur_pfid');
    var ids = $.trim($('#sharenums').val());
    var is_fund = $("#is_fund").prop('checked');
    localStorage.setItem('sharenums_'+cur_pfid,ids);
    localStorage.setItem('is_fund_'+cur_pfid,is_fund?1:0);
}


function parsenums () {
    var ids = $.trim($('#sharenums').val());
    var is_fund = $("#is_fund").prop('checked');

    if(ids.length === 0) {
        return [];
    }

    if(is_fund) {
        var qs = $.map(ids.match(/[0-9]{6}/g), function(v) { return 'f_'+v; });
    }else{
        var qs = $.map(ids.match(/[0-9]{6}/g), function(v) {
            var marketsig = parseInt(v.substr(0,1));
            var pfx = marketsig>=5?'s_sh':'s_sz';
            return pfx+v;
        });
    }

    return qs;
}

function updatetable() {

    var qs = parsenums();
    var is_fund = $("#is_fund").prop('checked');

    var dataSet = $.map(qs, function (v) {
        var val = localStorage.getItem(v);
        if(val !== null) {
            var dt = val.split(',');
            dt.push(v);
            return [dt];
        }
    });

    $("#data_table_tb").slideUp();

    if($.fn.dataTable.isDataTable("#data_table_tb")) {
        $("#data_table_tb").DataTable().destroy();
        $("#data_table_tb").empty();
    }

    if(is_fund) {

        var colm_defs = [ ];
        var colms = [
            { "title": "名称", "className":"dt-nowrap",
                "render": function ( data, type, row ) { return '<a data-code="'+row[6]+'" class="val_target" href="#">'+data+'</a>'; },},
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

        var colm_defs = [ ];
        var colms = [
            { "title": "名称", "className":"dt-nowrap",
                "render": function ( data, type, row ) { return '<a data-code="'+row[6]+'" class="val_target" href="#">'+data+'</a>'; },},
            { "title": "现价" },
            { "title": "涨跌" },
            { "title": "涨跌幅%",
                "render": function ( data, type, row ) { return data+'%'; },
            },
            { "title": "现量", "visible": false },
            { "title": "现手", "visible": false }
        ];
    }
 
    $("#data_table_tb").dataTable( {
        "paging":   false,
        "ordering": false,
        "info":     false,
        "searching":false,
        "data": dataSet,
        "columns": colms
    }).slideDown();

    $("#data_table_tb").DataTable().rows().every( function () {
        var row = this.data();

        var incr = 0;
        if(is_fund) {
            incr = parseFloat(row[1]) - parseFloat(row[3]);;
        } else {
            incr = parseFloat(row[2]);
        }


        if(incr > 0) {
            $(this.node()).addClass('reddata');
        } else if (incr < 0) {
            $(this.node()).addClass('greendata');
        }

    });

}

$(function () {

    $('#update_share').click(function(evn) {
        evn.preventDefault();
        $("#msgbar").text('Loading ...').slideDown();
        var qs = parsenums();

        if(qs.length > 0) {
            var qsstr = 'list='+qs.join(',');
            $.getScript('api.php?'+qsstr, function () {
                $.each(qs, function (i,v) {
                    localStorage.setItem(v, window['hq_str_'+v]);
                });
                updatetable();
                $("#msgbar").slideUp();
            });
        }

        //console.log(qs);
    });

    $(".profile_btn").click(function(evn) {
        evn.preventDefault();
        var btn = $(evn.target)
        var cur_pfid = btn.data("pfid");
        var lo_cur_pfid = localStorage.getItem('cur_pfid');

        if (lo_cur_pfid !== cur_pfid) {

            $(".profile_btn").removeClass('button-primary');
            btn.addClass('button-primary');

            localStorage.setItem('cur_pfid', cur_pfid);
            resumenums();
            updatetable();
        }
    });

    $("#neat_value").click(function() {
        var tb = $("#data_table_tb").DataTable();
        var dt = tb.column(1).data();
        var netv = $("#neat_val").empty().text(dt.join('\n'));
        $("#neat_val_window").modal({
            opacity:80,
            overlayCss: {backgroundColor:"#333"},
            minHeight:400,
            minWidth: 100,
        });

    });

    $("#data_table_div tbody").on('click', 'a.val_target', function(evn) {
        evn.preventDefault();

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
    });
});
