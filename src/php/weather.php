<?php include("../header.htm"); ?>
<?php include("header_edges.htm"); ?>

<script language="javascript">

function checkSubmit(e)
{
  if(e && e.keyCode == 13)
  {
    document.getElementById("day_form").submit();
  }
}
</script>

<h3>enter day</h3>

<form action="" method="get" id="day_form">
Enter the year and day (YYYY_DOY): 
<input id="date_string" type="text" name="datestr" value="<? echo $_GET['datestr'] ?>" 
onkeypress="checkSubmit(event)">
<input type="submit" value="Go">
</form>


<?php 

  if (!isset($_GET["datestr"])) {

  } else {

    $datestr = $_GET["datestr"];
    $year = substr($datestr, 0, 4);
    $doy = substr($datestr, 5, 3);
    $date = new DateTime($year . "-1-1");
    $date->modify("+".($doy-1) . " days");
// 370x330 div, 352x286 video
    echo "<h3>showing day: " . $datestr . " (" . $date->format('Y-M-d') . ")</h3>\n"; 
    echo "<div style='clear:both;'><h4>weather</h4><hr /></div>";
    echo "<div style='float:left; margin:8px;'>\n";
    echo "<video width='200' height='200' controls='' src='" . $datestr . "_camera_3.webm'></video>\n";
    echo "</div>\n";
    echo "<div style='float:left; margin:8px;'>\n";
    echo "<video width='356' height='200' controls='' src='" . $datestr . "_camera_2.webm'></video>\n";
    echo "</div>\n";
    echo "<div style='float:left; margin:8px;'>\n";
    echo "<video width='246' height='200' controls='' src='" . $datestr . "_camera_1.webm'></video>\n";
    echo "</div>\n";
    echo "<div style='clear:both; margin:8px;'>\n";
    echo "<a href='" . $datestr . "_weather.png'><img src='" . $datestr . "_weather.png' width='576' height='432' border='0'></a>\n";
    echo "</div>\n";
    echo "<div style='clear:both;'>+ <a href='day.php?datestr=" . $datestr . "'>View all plots for " . $datestr . " (" . $date->format('Y-M-d') . ")</a><br></div>\n";
  }

?>

<?php include("../footer.htm"); ?>

