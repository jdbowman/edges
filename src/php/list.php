<?php include("../header.htm"); ?>
<?php include("header_edges.htm"); ?>

<?php 

  $last_year = -1;
  echo "<h3>list of all data (excludes daily summaries)</h3>\n"; 

  echo "<table padding='0' spacing='0' border='0'>";

  foreach (array_reverse(glob($datestr . "*_Ta.png")) as $filename) {

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
    //$files['webcam'] = $filebase . "_webcam.webm";

    if ($last_year != strval($year)) {
      echo "<tr><td colspan='9'><h4>" . $year . "</h4><hr /></td></tr>\n";
      $last_year = $year;
    }

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

  echo "</table>\n";
  echo "<div style='clear:both;'><br /></div>\n";

?>

<?php include("../footer.htm"); ?>
