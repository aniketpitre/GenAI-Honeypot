```bash
# RunID:714782 Date:2025-10-11T18:09:32.440079
1  sudo apt update
2  sudo apt upgrade
3  sudo apt install vim
4  vi /etc/apt/sources.list.d/nginx.list  #Adding the nginx repo
5  sudo apt update
6  sudo apt install nginx
7  sudo systemctl status nginx
8  sudo systemctl start nginx
9  sudo systemctl enable nginx
10 sudo ufw allow 'Nginx HTTP'
11 sudo ufw allow 'Nginx HTTPS'
12 sudo ufw status
13 cd /var/www/html
14 sudo rm index.nginx-debian.html
15 sudo vi index.html
16 sudo systemctl restart nginx
17 curl http://localhost
18 ping google.com #Verifying internet connection, unrelated to web server
19 cat /var/log/nginx/access.log
20 cat /var/log/nginx/error.log
21 tail -f /var/log/nginx/access.log
22 sudo tail -f /var/log/nginx/error.log
23 sudo journalctl -u nginx
24 sudo journalctl -u nginx -f
25 sudo systemctl stop nginx
26 sudo apt remove nginx
27 sudo apt purge nginx
28 sudo apt autoremove
29 sudo apt update
30 sudo apt install nginx
31 sudo systemctl start nginx
32 sudo systemctl status nginx
33 sudo vi /etc/nginx/sites-available/default
34 sudo ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/
35 sudo systemctl restart nginx
36 nginx -t #Testing the configuration
37 sudo nginx -t
38 sudo systemctl reload nginx
39 sudo systemctl status nginx
40 sudo apt install php-fpm php-mysql
41 sudo vi /etc/nginx/sites-available/default #Configuring PHP
42 sudo systemctl restart nginx
43 sudo vi /var/www/html/info.php
44 curl http://localhost/info.php
45 sudo systemctl restart php7.4-fpm #Typo, correct below
46 sudo systemctl restart php8.1-fpm #Assuming PHP 8.1
47 sudo systemctl status php8.1-fpm
48 sudo apt install mysql-server
49 sudo mysql_secure_installation #Securing MySQL
50 sudo mysql -u root -p
51 SHOW DATABASES;
52 CREATE DATABASE mydatabase;
53 CREATE USER 'myuser'@'localhost' IDENTIFIED BY 'mypassword';
54 GRANT ALL PRIVILEGES ON mydatabase.* TO 'myuser'@'localhost';
55 FLUSH PRIVILEGES;
56 exit
57 sudo ufw allow 3306
58 sudo ufw status
59 sudo systemctl restart mysql
60 sudo systemctl status mysql
61 sudo adduser newuser
62 sudo usermod -aG sudo newuser
63 su - newuser
64 id
65 exit
66 sudo passwd newuser
67 sudo chown www-data:www-data /var/www/html -R
68 sudo chmod 755 /var/www/html -R
69 df -h #Checking disk space
70 du -hsx * | sort -rh | head -10 #Finding large directories
71 sudo find / -type f -size +100M #Finding large files
72 sudo apt clean
73 sudo apt autoclean
74 sudo systemctl restart logrotate
75 sudo logrotate -f /etc/logrotate.conf
76 sudo apt update && sudo apt upgrade
77 history
```