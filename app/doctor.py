import shutil


def check (program):
    return shutil.which(program) is not None 



def doctor(): 
    report = []
    
    report.append("========== SOUNIX DOCTOR ==========")


    report.append(
        "✓ python 3" if check("python3") else "✗ python 3"
    )

    report.append(
        "✓ git" if check ("git") else "✗ git"
    )



    report.append(
        "✓ ClamAV"
        if check ("clamscan") or check ("clamd")
        else "✗ ClamAV"
     )


    report.append(
        "✓ firewall (UFW)"
         if check ("ufw")
         else "✗ firewall (UFW)" 
    )

    report.append( 
        "✓ wireguard"
        if check ("wg")
        else "✗ wireguard"
    )

    report.append( 
        "✓ Nmap"
        if check ("nmap")
        else "✗ Nmap"
   )

    report.append(
       "✓ tcpdump"
       if check ("tcpdump")
       else "✗ tcpdump"
   )

    report.append(
       "✓ Wireshark"
      if check ("wireshark")
      else "✗ wireshark"
   )


    
    report.append("===================================")

    return "\n".join(report)  
