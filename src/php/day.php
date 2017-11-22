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

    echo "<h3>showing day: " . htmlspecialchars($datestr) . " (" . $date->format('Y-M-d') . ")</h3>\n"; 

    echo "<div style='clear:both;'><h4>images</h4><hr /></div>";

    foreach (glob($datestr . "*.png") as $filename) {
      echo "<div style='width:800px;padding:10px;clear:both;'>\n";
      echo "<div style='width:250px;padding:5px;float:left;'>\n";
      echo "<a href='" . $filename . "'><image src='" . $filename . "' border='0' 
width='230'></a>\n";
      echo "</div><div sytle='width:500px;padding:5px;float:left;'>\n";
      echo "<p style='font-size:160%;'>" . $filename . "</p>\n";
      echo "<p><i>size:</i> " . sprintf("%01.0f", filesize($filename)/1000) . " kB<br />\n";
      echo "<i>last modified:</i> " . date ("F d Y H:i:s", filemtime($filename)) . "</p>\n";
      echo "</div></div>\n";
    }

    echo "<div style='clear:both;'><h4>videos</h4><hr /></div>";

    foreach (glob($datestr . "*.webm") as $filename) {
      echo "<div style='width:800px;padding:10px;clear:both;'>\n";
      echo "<div style='width:250px;padding:5px;float:left;'>\n";
      echo "<video src='" . $filename . "' controls=''  width='230'></video>\n";
      echo "</div><div sytle='width:500px;padding:5px;float:left;'>\n";
      echo "<p style='font-size:160%;'>" . $filename . "</p>\n";
      echo "<p><i>size:</i> " . sprintf("%01.0f", filesize($filename)/1000) . " kB<br />\n";
      echo "<i>last modified:</i> " . date ("F d Y H:i:s", filemtime($filename)) . "</p>\n";
      echo "</div></div>\n";
    }


    echo "<div style='clear:both;'><br /></div>";

  }



?>

<?php include("../footer.htm"); ?>
