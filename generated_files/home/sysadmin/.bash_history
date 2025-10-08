```bash
history -c
date
uptime
top -b -n 1 | head -n 15
free -m
df -h
du -hsx /* | sort -rh | head -10
apt update
apt upgrade -y
apt autoremove -y
apt install -y htop iotop nmap
htop
iotop
ss -tulpn
netstat -tulpn # forgot ss is newer
ss -tulpn | grep 80
ss -tulpn | grep 443
ufw status
ufw enable # oops, forgot to configure first
ufw allow 80
ufw allow 443
ufw reload
ufw status
tail /var/log/auth.log
tail -f /var/log/auth.log # watching logins
ssh user@internal_server # jumping to another server
exit
su -
cd /var/log/apache2/
ls -l
tail -f access.log # check access log
tail -f error.log # check error log
grep "404" error.log # look for not found errors
grep "PHP Warning" error.log # check PHP warnings
grep "POST" access.log | awk '{print $1}' | sort | uniq -c | sort -nr | head -10 # Top POSTing IPs
cd /etc/apache2/
ls -l
nano apache2.conf # edit the main config
apachectl -t # check config syntax
systemctl restart apache2 # restart apache
systemctl status apache2
systemctl stop apache2
systemctl start apache2 # started back up
systemctl reload apache2
grep ServerName sites-available/* # Finding virtualhosts
cd sites-available/
ls -l
cat 000-default.conf
cat example.com.conf
nano example.com.conf # made a change to virtualhost
apachectl -t
systemctl reload apache2
a2enmod headers # enable a module
a2dismod status # disable status page for now
apachectl -t
systemctl reload apache2
adduser newuser
passwd newuser
usermod -aG www-data newuser # add user to www-data group
chown -R www-data:www-data /var/www/example.com/ # fix permissions
find /var/www/example.com/ -type f -exec chmod 644 {} \;
find /var/www/example.com/ -type d -exec chmod 755 {} \;
chmod +x /var/www/example.com/scripts/backup.sh # make a script executable
chmod 700 /var/www/example.com/scripts/backup.sh # more restrictive
ls -l /var/www/example.com/scripts/backup.sh
crontab -e
nano /etc/logrotate.d/apache2 # edit log rotation
date
ntpq -p
timedatectl
timedatectl set-timezone America/Los_Angeles
timedatectl status
apt install -y fail2ban
fail2ban-client status
fail2ban-client stop apache-auth
fail2ban-client start apache-auth # restarts jail
fail2ban-client status apache-auth
iptables -L # check iptables (fail2ban changes them)
apt install -y letsencrypt
letsencrypt certonly --webroot -w /var/www/example.com -d example.com -d www.example.com # getting cert
cd /etc/apache2/sites-available/
cp example.com.conf example.com-ssl.conf # copy to ssl version
nano example.com-ssl.conf # configure ssl virtualhost
apachectl -t
a2ensite example.com-ssl.conf
systemctl reload apache2
ufw allow 443
ufw reload
ufw status
certbot renew --dry-run # testing renewal
certbot renew
history
```