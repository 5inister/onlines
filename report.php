<?php
/*Recieve a json object and write it into the json file correspondoing to today's date
in the relevant user directory*/
$dir=$_POST['user'];
echo 'user: '.$dir.' ';
$py_json=$_POST['json'];#From mainSniffer submitReport
echo 'json: '.$py_json.'.';
$data = json_decode($py_json);
$today=date('d_m_Y');
$file=$today.'.json';
if (file_exists($dir.'/'.$file)){
    $existingJson = json_decode(file_get_contents($dir.'/'.$file), true);
}else{
    $existingJson=array();
}
array_push($existingJson,$data);
$outfile=fopen($dir.'/'.$file,"w");
fwrite($outfile,json_encode($existingJson));
echo '1';
?>