$(function() {
    resumenums();
    $('#sharenums').blur(savenums);
    $('#is_fund').click(savenums);
});

function resumenums () {
    var cur_pfid = localStorage.getItem('cur_pfid');
    if(cur_pfid === null) {
        cur_pfid = '1';
        localStorage.setItem('cur_pfid',cur_pfid);
    }

    $("#cur_pfid").text(cur_pfid);

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
            return [val.split(',')];
        }
    });

    $("#data_table").html( '<table cellpadding="0" cellspacing="0" border="0" class="display" id="data_table_tb"></table>' );

    if(is_fund) {

        var colm_defs = [];
        var colms = [
            { "title": "名称" },
            { "title": "净值" },
            { "title": "？？" },
            { "title": "昨净" },
            { "title": "净值日期" },
            { "title": "？？" },
        ];

    } else {

        var colm_defs = [
            { "render": function ( data, type, row ) { return '￥'+data; }, "targets": [1,2] },
            { "render": function ( data, type, row ) { return data+'%'; }, "targets": 3 }
        ];
        var colms = [
            { "title": "名称" },
            { "title": "现价" },
            { "title": "涨跌" },
            { "title": "涨跌幅%" },
            { "title": "现量" },
            { "title": "现手" },
        ];
    }
 
    var tb = $("#data_table_tb").dataTable( {
        "data": dataSet,
        "paging":   false,
        "ordering": false,
        "info":     false,
        "searching":false,
        "columnDefs": colm_defs,
        "columns": colms
    });


    $("#test_tbn").click(function(env) {

        console.log(tb.column(3).data());


    });

}

$(function () {

    $('#update_share').click(function(evn) {
        evn.preventDefault();
        var qs = parsenums();
        var qsstr = 'list='+qs.join(',');
        $.getScript('api.php?'+qsstr, function () {
            $.each(qs, function (i,v) {
                localStorage.setItem(v, window['hq_str_'+v]);
            });
            updatetable();
        });


        //console.log(qs);
    });

    $(".profile_btn").click(function(evn) {
        evn.preventDefault();
        var cur_pfid = $(evn.target).data("pfid");
        var lo_cur_pfid = localStorage.getItem('cur_pfid');

        if (lo_cur_pfid !== cur_pfid) {
            localStorage.setItem('cur_pfid', cur_pfid);
            resumenums();
            updatetable();
        }
    });

});
