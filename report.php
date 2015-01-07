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
if (file_exists($dir.'_json/'.$file)){
    chmod($dir.'_json/'.$file,0766);           
    $existingJson = json_decode(file_get_contents($dir.'_json/'.$file), true);
    while ($existingJson[0]==null){
		$existingJson = json_decode(file_get_contents($dir.'_json/'.$file), true);
	}
}else{
    $existingJson=array();
}
array_push($existingJson,$data);
$outfile=fopen($dir.'_json/'.$file,"w");
fwrite($outfile,json_encode($existingJson));
fclose($outfile);
$just_written_json=json_decode(file_get_contents($dir.'_json/'.$file), true);
while($just_written_json[0] == null){
    $outfile = fopen($file,"w");
    fwrite( $outfile, json_encode($existingJson));
    fclose($outfile);
    $just_written_json=json_decode(file_get_contents($dir.'_json/'.$file), true);
}

?>
