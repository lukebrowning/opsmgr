#--- Monitoring commands for OpsMgr role: osa_host

command[osa_host_cpu] = /etc/nagios/plugins/check-cpu.rb -w 80 -c 90
command[osa_host_mem] = /etc/nagios/plugins/check-mem.sh -w 250 -c 100
command[osa_host_disk] = /etc/nagios/plugins/check-disk.rb 
command[osa_host_large_files] = /etc/nagios/plugins/check-for-large-files.sh -d /var/log -s 1048576
command[osa_host_slsocket] = /etc/nagios/plugins/check-syslog-socket.rb 
command[osa_host_ntp] = /etc/nagios/plugins/check-ntp.rb 
command[osa_host_eth10] = /etc/nagios/plugins/check-netif.rb -c 500 -w 350 --interfaces eth10
command[osa_host_eth11] = /etc/nagios/plugins/check-netif.rb -c 500 -w 350 --interfaces eth11
command[osa_host_ntpd] = /etc/nagios/plugins/check-procs.rb -p ntpd -w 30 -c 40 -W 1 -C 1
command[osa_host_rsyslogd] = /etc/nagios/plugins/check-procs.rb -p rsyslogd -w 30 -c 40 -W 1 -C 1
command[osa_host_beaver]  = /etc/nagios/plugins/check-procs.rb -p beaver -w 100 -c 120 -W 1 -C 1
command[osa_host_sshd] = /etc/nagios/plugins/check-procs.rb -p sshd -w 30 -c 40 -W 1 -C 1
command[osa_host_cron] = /etc/nagios/plugins/check-procs.rb -p cron -w 30 -c 40 -W 1 -C 1
command[osa_host_dbus] = /etc/nagios/plugins/check-procs.rb -p dbus-daemon -w 30 -c 40 -W 1 -C 1
command[osa_host_rcu] = /etc/nagios/plugins/check-procs.rb -p rcu -w 30 -c 40 -W 1 -C 1

