<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Control Panel</title>
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.0/jquery.min.js" type="text/javascript" charset="utf-8"></script>
<style type="text/css">

* {
    margin: 0;
    padding: 0;
}

body {
    background-color: #eee;

}

a:link, a:visited {
    color: #000;
    text-decoration:none;
}

#tasks {
    margin: 5px;
    padding: 5px;
    background-color: #ddd;
    float: left;
    width: 30%;
    min-height:480px;
}

#tasks ul li{
    margin: 10px 5px 5px 20px;
    background-color: #ccc;
}

#tasks ul li a{
    margin-left: 3px;
    font-size: 12px;
}
#tasks ul li a em{
    margin: 3px;
    float: right;
}


#control {
    margin: 5px;
    padding: 5px;
    float: left;
    width: 65%;
    background-color: #ddd;
    min-height:480px;
}

.logwindow {
    margin: 10px 0;
    font-family:monospace;
    overflow-y: scroll;
    background-color: #ccc;
    height: 380px;
}

</style>
<script type="text/javascript">

$(function () {

    $.get("http://localhost:8080/list_all_tasks", function(data){console.log(data);}).success(function (data) {
        console.log(data);
    });
    //$("#tasks ul").append($("<li>test</li>"));

});

</script>
</head>

<body>

<div id="tasks">
    <ul>
        <li><a href="#">TaskName <em>Runnging</em></a></li>
        <li><a href="#">TaskName <em>Runnging</em></a></li>
        <li><a href="#">TaskName <em>Runnging</em></a></li>
        <li><a href="#">TaskName <em>Runnging</em></a></li>
        <li><a href="#">TaskName <em>Runnging</em></a></li>
        <li><a href="#">TaskName <em>Runnging</em></a></li>
        <li><a href="#">TaskName <em>Runnging</em></a></li>
        <li><a href="#">TaskName <em>Runnging</em></a></li>
        <li><a href="#">TaskName <em>Runnging</em></a></li>
        <li><a href="#">TaskName <em>Runnging</em></a></li>
    </ul>
</div>

<div id="control">
    <div id="taskinfo">
        <h2>TaskName</h2>
        <div class="logwindow">
            <p>
            test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br /> test <br />
            </p>
        </div>
    </div>
</div>

</body>
</html>

