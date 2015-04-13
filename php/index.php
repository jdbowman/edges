<?php include("../header.htm"); ?>
<?php include("header_edges.htm"); ?>

<?php 

  $recent = array_reverse(glob("*_Ta.png"));
  $recent_weather = array_slice(array_reverse(glob("*_weather.png")), 0, 1);


  //////////////////////
  // Show latest spectra
  //////////////////////

  echo "<div style='clear:both;'><h3>latest spectra</h3>\n"; 

  foreach (array_slice($recent, 0, 2) as $filename) {

    $filebase = substr($filename, 0, 11);
    $datestr = substr($filename, 0, 8);
    $year = substr($filename, 0, 4);
    $doy = substr($filename, 5, 3);
    $date1 = new DateTime($year . "-1-1");
    $date1->modify("+".($doy-1) . " days");

    echo "<div style='float:left; width:410px'>\n";
    echo "<p style='margin:0px;'>" . $filebase . " (<a href='day.php?datestr=" . $datestr . "'>" . $date1->format("Y-M-d") . "</a>)</p>";
    echo "<a href='" . $filename . "'><img src='" . $filename . "' border='0' width='400'></a><br />\n</div>\n";
  }
  echo "</div>\n";



  //////////////////////
  // Show latest weather
  //////////////////////

  $datestr = substr($recent_weather[0], 0, 8);
  $year = substr($recent_weather[0], 0, 4);
  $doy = substr($recent_weather[0], 5, 3);
  $date2 = new DateTime($year . "-1-1");
  $date2->modify("+".($doy-1) . " days");
  echo "<div style='clear:both;padding: 20px 0px 0px 0px;'><h3>latest weather: " . $datestr . " (<a href='day.php?datestr=" . $datestr . "'>". $date2->format("Y-M-d") . "</a>)</h3>\n"; 
  echo "<div style='float:left; width:370px;'>\n";
  echo "<video width='352' height='286' controls='' src='" . $datestr . "_webcam.webm'></video>\n";
  echo "</div>\n";
  echo "<div style='float:left; width:460px;'>\n";
  echo "<a href='" . $datestr . "_weather.png'><img src='" . $datestr . "_weather.png' height='300' border='0'></a>\n";
  echo "</div>\n";


  ///////////////////
  // List recent data
  ///////////////////

  echo "<div style='clear:both;padding: 20px 0px 0px 0px;'><h3>list of recent data (excludes daily summaries)</h3>\n"; 
  echo "<table padding='0' spacing='0' border='0'>";

  foreach (array_slice($recent, 0, 10) as $filename) {

    $year = substr($filename, 0, 4);
    $doy = substr($filename, 5, 3);
    $date = new DateTime($year . "-1-1");
    $date->modify("+".($doy-1) . " days");
    $filebase = substr($filename, 0, 11);
    $files['Ta (uncorrected)'] = $filebase . "_Ta.png";
    $files['p0 (antenna)'] = $filebase . "_p0.png";
    $files['p1 (cold)'] = $filebase . "_p1.png";
    $files['p2 (hot)'] = $filebase . "_p2.png";
    $files['rfi'] = $filebase . "_rfi.png";
    $files['power'] = $filebase . "_power.png";
    $files['thermal'] = $filebase . "_temps.png";
    $files['webcam'] = $filebase . "_webcam.webm";

    echo "<tr><td>" . $filebase . " &nbsp; (<a href='day.php?datestr=" . $year . "_" . $doy . "'>" . $date->format("Y-M-d") ."</a>) &nbsp; </td>";

    foreach ($files as $key => $file) {
   
      if (file_exists($file)) {
        echo "<td> &nbsp; <a href='" . $file . "'>" . $key . "</a></td> ";
      } else {
        echo "<td> &nbsp; <font color='#e0e0e0'>" . $key . "</font></td> ";
      }
    }

    echo "</tr>\n";
  }

  echo "</table></div>\n<p>+ <a href='list.php'>List all data</a></p>";
  echo "<div style='clear:both;'><br /></div>\n";

?>

<?php include("../footer.htm"); ?>
