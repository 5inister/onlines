<?php
header("Access-Control-Allow-Origin: *"); //Allow Cross Origin (CORS)
$time = time();
$data_path='dial.json';
$data=file_get_contents($data_path);
$data_md5=md5_file($data_path); //Generate md5 checksum for original file
$last_hash=$data_md5;
$delta_time=0;
while ($delta_time < 30){ //Wait 30 seconds for file to change
      $data_md5=md5_file($data_path);
      //Check if file has changed by comparing current checksum to previous one
      if ($data_md5 !== $last_hash){ 
      	 $data =file_get_contents($data_path);
	 $last_hash = $data_md5;
	 break;
      }
      $delta_time=time()-$time;      
}
echo $data;
?>
