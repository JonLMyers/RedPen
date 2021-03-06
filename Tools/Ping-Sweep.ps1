$Address = Read-Host -Prompt 'Enter Starting IP Address'
$Cidr = Read-Host -Prompt 'Enter Subnet(CIDR)'

[int]$timeout = 20
[switch]$resolve = $true
[int]$TTL = 128
[switch]$DontFragment = $false
[int]$buffersize = 32
$options = new-object system.net.networkinformation.pingoptions
$options.TTL = $TTL
$options.DontFragment = $DontFragment
$buffer=([system.text.encoding]::ASCII).getbytes("a"*$buffersize)

function IP-toINT64 () { 
  param ($Address) 
  
  $octets = $Address.split(".") 
  return [int64]([int64]$octets[0]*16777216 +[int64]$octets[1]*65536 +[int64]$octets[2]*256 +[int64]$octets[3]) 
} 
 
function INT64-toIP() { 
  param ([int64]$int) 

  return (([math]::truncate($int/16777216)).tostring()+"."+([math]::truncate(($int%16777216)/65536)).tostring()+"."+([math]::truncate(($int%65536)/256)).tostring()+"."+([math]::truncate($int%256)).tostring() )
} 

if ($Address) {$ipaddr = [Net.IPAddress]::Parse($Address)} 
if ($Cidr) {$maskaddr = [Net.IPAddress]::Parse((INT64-toIP -int ([convert]::ToInt64(("1"*$Cidr+"0"*(32-$Cidr)),2)))) } 
if ($Address) {$networkaddr = new-object net.ipaddress ($maskaddr.address -band $ipaddr.address)} 
if ($Address) {$broadcastaddr = new-object net.ipaddress (([system.net.ipaddress]::parse("255.255.255.255").address -bxor $maskaddr.address -bor $networkaddr.address))} 
 
if ($Address) { 
  $startaddr = IP-toINT64 -Address $networkaddr.ipaddresstostring 
  $endaddr = IP-toINT64 -Address $broadcastaddr.ipaddresstostring 
}
 
$ping = new-object system.net.networkinformation.ping
for ($i = $startaddr; $i -le $endaddr; $i++) 
{ 
  INT64-toIP -int $i 
  #test-connection -ComputerName ( INT64-toIP -int $i ) -Quiet -Count 2 -TTL 20
  try
  {
    $reply = $ping.Send((INT64-toIP -int $i),$timeout,$buffer,$options)
  }
  catch
  {
    $ErrorMessage =$_.ExceptionMessage
  }
  if ($reply.status -eq "Success")
  {
    Write-Host "Host exists and is online."
  }
  else
  {
    Write-Host "Host does not exist or is not online."
  }
  Write-Host "----------------------------"
}
