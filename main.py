# IHK Lehrstellen Caller
# Entwickelt von Ashkan Navid - Jan 2020

# TO-DO Liste:
#   - Suchkriterien erweitern
#   - GUI Erstellen
#   - An webserver optimieren (Flask o.ä.)

import requests as req
from bs4 import BeautifulSoup as soup
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import datetime
import sys

################################################################################
# Veränderbare Variablen
# ------------------------------------------------------------------------------
# RECEIVER NAME | Dein Vorname
receiver_name = 'YOURNAME'
# EMPFAENGER | Deine E-Mail Adresse
empfaenger = 'YOURMAIL'
# LOCATION | Postleitzahl
location = 12345
# PERIMETER | Umkreis
perimeter = 20
# QUERY RAW | Ausbildungsberuf (Abgekürze Variante benutzen! Bsp: Kfm/Kffr für Büromanagement)
query_raw = 'Kfm/Kffr für Büromanagement'
# DELAY | Pause bis zum Versand der nächsten E-Mail (in Sekunden! 3600 = 1 Stunde)
delay = 3600
# MAX SEARCH | Anzahl der angezeigten Ausbildungsstellen in der E-Mail (1 - 50)
max_search = 10
# SORT MODE | Sortierung der Liste (-1 = Normale Listung)
sort_mode = '-1'
# SMTP SERVER | SMTP Server Adresse
smtp_server = 'SMTPADDRESS'
# SMTP PORT | SMTP Serverport
smtp_port = 25
# SMTP USER | SMTP Benutzername zum E-Mail Konto (ggf. identisch mit SENDERMAIL)
smtp_user = 'SMTPUSER'
# SMTP PASS | SMTP Passwort zum E-Mail Konto
smtp_pass = 'SMTPPASS'
# SENDERMAIL | E-Mail Adresse welche als Sender verwendet wird (ggf. identisch mit SMTP USER)
sendermail = 'SMTPMAIL'
################################################################################


class InvalidMaxSearch(Exception):
    pass


class InvalidDelayTime(Exception):
    pass


class InvalidJobName(Exception):
    pass


class InvalidPerimeter(Exception):
    pass


if max_search <= 0 or max_search > 50:
    raise InvalidMaxSearch('Please choose a max_search from 1 to 50!')

if delay <= 0:
    raise InvalidDelayTime('Please choose a valid delay time!')

if query_raw == 'Kfm/Kffr für Büromanagement':
    query = 'Kaufmann%2F-frau+f%C3%BCr+B%C3%BCromanagement'
else:
    raise InvalidJobName('Please enter a valid jobname!')

if perimeter == 20:
    distance = 1
elif perimeter == 50:
    distance = 2
elif perimeter == 100:
    distance = 3
elif perimeter == 150:
    distance = 4
else:
    raise InvalidPerimeter('Please enter a valid perimeter!')


class IHKBot:
    def __init__(self, url, smtp_server, smtp_port, smtp_user, smtp_pass):
        self.url = url
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass
        print('Bot instance created successfully!')

    def request_site(self):
        print('Requested site: ' + self.url)
        return req.get(self.url)

    def send_mail(self, subject, message, sender, receiver):
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.login(self.smtp_user, self.smtp_pass)
            server.sendmail(
                sender, receiver, message.as_string().encode('utf-8')
            )
            print('E-Mail was sent successfully to ' + receiver)


bot = IHKBot(
    'https://www.ihk-lehrstellenboerse.de/angebote/suche?query=' + query +
    '&qualification=-1&sortColumn=' + sort_mode + '&location=' + str(location) + '&distance=' + str(distance) + '&thisYear=true&_thisYear=on&_nextYear=on&_afterNextYear=on'
    '&organisationName=Unternehmen+eingeben&submit=Suchen',
    smtp_server,
    smtp_port,
    smtp_user,
    smtp_pass)

start_printing = False  # Intern
counter = 0  # Intern
job = 1  # Intern
jobs = [('Beruf', []), ('Ort', []), ('Entfernung', []), ('Unternehmen', []), ('Freie Plätze', []),
        ('Ausbildungsnummer', [])]

while True:
    doc = soup(bot.request_site().text, 'html.parser')
    table = doc.find_all('a')

    print('Extracting information from site...')

    for element in table:
        text = element.text.strip()
        href = element.attrs['href']
        if 'ausbildung' in href:
            ausbildungs_nr = href.split('/')[3]
        else:
            ausbildungs_nr = -1

        if text == 'Plätze':
            start_printing = True
            continue
        elif text == 'zum Anfang':
            start_printing = False
        elif start_printing:
            if counter >= 5:
                job += 1
                counter = 0

            if counter == 0:
                jobs[counter][1].append(text)

            if counter == 1:
                jobs[counter][1].append(text)

            if counter == 2:
                jobs[counter][1].append(text)

            if counter == 3:
                jobs[counter][1].append(text)

            if counter == 4:
                jobs[counter][1].append(text)
                jobs[counter + 1][1].append(ausbildungs_nr)

            counter += 1

    Dict = {title: column for (title, column) in jobs}
    df = pd.DataFrame(Dict)

    print('Extracted all informations successfully!')

    search_limit = """\
    """

    for i in range(0, max_search):
        new_block = """\
            <tr>
                <td class="align-center">""" + str(jobs[0][1][i]) + """</td>
                <td class="align-center">""" + str(jobs[3][1][i]) + """</td>
                <td class="align-center">""" + str(jobs[1][1][i]) + """</td>
                <td class="align-center">""" + str(jobs[4][1][i]) + """</td>
                <td class="align-center btn btn-primary"><a href="https://www.ihk-lehrstellenboerse.de/suche?query=""" + str(
            jobs[5][1][i]) + """">Zur Stelle</a></td>
            </tr>
            """
        search_limit = search_limit + new_block

    html = """\
        <!doctype html>
        <html>

        <head>
            <meta name="viewport" content="width=device-width" />
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <title>IHK Lehrstellenbörsen Abruf</title>
            <style>
                /* -------------------------------------
                      GLOBAL RESETS
                  ------------------------------------- */

                /*All the styling goes here*/

                img {
                    border: none;
                    -ms-interpolation-mode: bicubic;
                    max-width: 100%;
                }

                body {
                    background-color: #f6f6f6;
                    font-family: San Francisco, San-Francisco, sf, Helvetica, sans-serif;
                    -webkit-font-smoothing: antialiased;
                    font-size: 14px;
                    line-height: 1.4;
                    margin: 0;
                    padding: 0;
                    -ms-text-size-adjust: 100%;
                    -webkit-text-size-adjust: 100%;
                }

                table {
                    border-collapse: separate;
                    mso-table-lspace: 0pt;
                    mso-table-rspace: 0pt;
                    width: 100%;
                }

                table td {
                    font-family: San Francisco, San-Francisco, sf, Helvetica, sans-serif;
                    font-size: 14px;
                    vertical-align: top;
                }

                /* -------------------------------------
                      BODY & CONTAINER
                  ------------------------------------- */

                .body {
                    background-color: #f6f6f6;
                    width: 100%;
                }

                /* Set a max-width, and make it display as block so it will automatically stretch to that width, but will also shrink down on a phone or something */
                .container {
                    display: block;
                    margin: 0 auto !important;
                    /* makes it centered */
                    max-width: 580px;
                    padding: 10px;
                    width: 580px;
                }

                /* This should also be a block element, so that it will fill 100% of the .container */
                .content {
                    box-sizing: border-box;
                    display: block;
                    margin: 0 auto;
                    max-width: 580px;
                    padding: 10px;
                }

                /* -------------------------------------
                      HEADER, FOOTER, MAIN
                  ------------------------------------- */
                .main {
                    background: #ffffff;
                    border-radius: 3px;
                    width: 100%;
                }

                .wrapper {
                    box-sizing: border-box;
                    padding: 20px;
                }

                .content-block {
                    padding-bottom: 10px;
                    padding-top: 10px;
                }

                .footer {
                    clear: both;
                    margin-top: 10px;
                    text-align: center;
                    width: 100%;
                }

                .footer td,
                .footer p,
                .footer span,
                .footer a {
                    color: #999999;
                    font-size: 12px;
                    text-align: center;
                }

                /* -------------------------------------
                      TYPOGRAPHY
                  ------------------------------------- */
                h1,
                h2,
                h3,
                h4 {
                    color: #000000;
                    font-family: San Francisco, San-Francisco, sf, Helvetica, sans-serif;
                    font-weight: 400;
                    line-height: 1.4;
                    margin: 0;
                    margin-bottom: 30px;
                }

                h1 {
                    font-size: 35px;
                    font-weight: 300;
                    text-align: center;
                    text-transform: capitalize;
                }

                p,
                ul,
                ol {
                    font-family: San Francisco, San-Francisco, sf, Helvetica, sans-serif;
                    font-size: 14px;
                    font-weight: normal;
                    margin: 0;
                    margin-bottom: 15px;
                }

                p li,
                ul li,
                ol li {
                    list-style-position: inside;
                    margin-left: 5px;
                }

                a {
                    color: #3498db;
                    text-decoration: underline;
                }

                /* -------------------------------------
                      BUTTONS
                  ------------------------------------- */
                .btn {
                    box-sizing: border-box;
                    width: 100%;
                }

                .btn>tbody>tr>td {
                    padding-bottom: 15px;
                }

                .btn table {
                    width: auto;
                }

                .btn table td {
                    background-color: #ffffff;
                    border-radius: 5px;
                    text-align: center;
                }

                .btn a {
                    background-color: #ffffff;
                    border: solid 1px #3498db;
                    border-radius: 5px;
                    box-sizing: border-box;
                    color: #3498db;
                    cursor: pointer;
                    display: inline-block;
                    font-size: 14px;
                    font-weight: bold;
                    margin: 0;
                    padding: 12px 25px;
                    text-decoration: none;
                    text-transform: capitalize;
                }

                .btn-primary table td {
                    background-color: #3498db;
                }

                .btn-primary a {
                    background-color: #3498db;
                    border-color: #3498db;
                    color: #ffffff;
                }

                /* -------------------------------------
                      OTHER STYLES THAT MIGHT BE USEFUL
                  ------------------------------------- */
                .last {
                    margin-bottom: 0;
                }

                .first {
                    margin-top: 0;
                }

                .align-center {
                    text-align: center;
                }

                .align-right {
                    text-align: right;
                }

                .align-left {
                    text-align: left;
                }

                .clear {
                    clear: both;
                }

                .mt0 {
                    margin-top: 0;
                }

                .mb0 {
                    margin-bottom: 0;
                }

                .preheader {
                    color: transparent;
                    display: none;
                    height: 0;
                    max-height: 0;
                    max-width: 0;
                    opacity: 0;
                    overflow: hidden;
                    mso-hide: all;
                    visibility: hidden;
                    width: 0;
                }

                .powered-by a {
                    text-decoration: none;
                }

                hr {
                    border: 0;
                    border-bottom: 1px solid #f6f6f6;
                    margin: 20px 0;
                }

                /* -------------------------------------
                      RESPONSIVE AND MOBILE FRIENDLY STYLES
                  ------------------------------------- */
                @media only screen and (max-width: 620px) {
                    table[class=body] h1 {
                        font-size: 28px !important;
                        margin-bottom: 10px !important;
                    }

                    table[class=body] p,
                    table[class=body] ul,
                    table[class=body] ol,
                    table[class=body] td,
                    table[class=body] span,
                    table[class=body] a {
                        font-size: 16px !important;
                    }

                    table[class=body] .wrapper,
                    table[class=body] .article {
                        padding: 10px !important;
                    }

                    table[class=body] .content {
                        padding: 0 !important;
                    }

                    table[class=body] .container {
                        padding: 0 !important;
                        width: 100% !important;
                    }

                    table[class=body] .main {
                        border-left-width: 0 !important;
                        border-radius: 0 !important;
                        border-right-width: 0 !important;
                    }

                    table[class=body] .btn table {
                        width: 100% !important;
                    }

                    table[class=body] .btn a {
                        width: 100% !important;
                    }

                    table[class=body] .img-responsive {
                        height: auto !important;
                        max-width: 100% !important;
                        width: auto !important;
                    }
                }

                /* -------------------------------------
                      PRESERVE THESE STYLES IN THE HEAD
                  ------------------------------------- */
                @media all {
                    .ExternalClass {
                        width: 100%;
                    }

                    .ExternalClass,
                    .ExternalClass p,
                    .ExternalClass span,
                    .ExternalClass font,
                    .ExternalClass td,
                    .ExternalClass div {
                        line-height: 100%;
                    }

                    .apple-link a {
                        color: inherit !important;
                        font-family: inherit !important;
                        font-size: inherit !important;
                        font-weight: inherit !important;
                        line-height: inherit !important;
                        text-decoration: none !important;
                    }

                    #MessageViewBody a {
                        color: inherit;
                        text-decoration: none;
                        font-size: inherit;
                        font-family: inherit;
                        font-weight: inherit;
                        line-height: inherit;
                    }

                    .btn-primary table td:hover {
                        background-color: #34495e !important;
                    }

                    .btn-primary a:hover {
                        background-color: #34495e !important;
                        border-color: #ffffff !important;
                    }
                }
            </style>
        </head>

        <body class="">
            <span class="preheader">Hier sind die neusten Ausbildungsstellen Auschreiben aus der Lehrstellenbörse der IHK</span>
            <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="body">
                <tr>
                    <td>&nbsp;</td>
                    <td class="container">
                        <div class="content">

                            <!-- START CENTERED WHITE CONTAINER -->
                            <table role="presentation" class="main">

                                <!-- START MAIN CONTENT AREA -->
                                <tr>
                                    <td class="wrapper">
                                        <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td>
                                                    <p><b>Hallo """ + receiver_name + """,</b></p>
                                                    <p class="align-center">Hier sind die ersten """ + str(max_search) + """ Ausbildungsstellen welche mithilfe deiner Sucheinstellungen gefunden wurden:</p>
                                                    <br><p class="align-center">""" + query_raw + """</p>
                                                    <p class="align-center">""" + str(perimeter) + """km Umkreis von """ + str(location) + """</p>
                                                    <table>
                                                        <tr>
                                                            <th>Beruf</th>
                                                            <th>Unternehmen</th>
                                                            <th>Ort</th>
                                                            <th>Freie Plätze</th>
                                                            <th>Ausbildungsnummer</th>
                                                        </tr>
                                                        """ + search_limit + """
                                                    </table>
                                                    <br>
                                                    <p class="align-center">Um zu dem Ausbildungsausschreiben zu gelangen, klicke einfach auf den nebenliegenden Button</p>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                                <!-- END MAIN CONTENT AREA -->
                            </table>
                            <!-- END CENTERED WHITE CONTAINER -->

                            <!-- START FOOTER -->
                            <div class="footer">
                                <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td class="content-block">
                                            <span class="apple-link">Informationen aus der Lehrstellenbörse der IHK entnommen</span>
                                            <br><a href="https://www.ihk-lehrstellenboerse.de/">IHK Lehrstellenbörse öffnen</a>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class="content-block powered-by">
                                            Entwickelt von Ashkan Navid
                                        </td>
                                    </tr>
                                </table>
                            </div>
                            <!-- END FOOTER -->

                        </div>
                    </td>
                    <td>&nbsp;</td>
                </tr>
            </table>
        </body>

        </html>
        """

    message = MIMEMultipart("alternative")
    message["Subject"] = 'IHK Lehrstellenbörsen Abruf'
    message["From"] = sendermail
    message["To"] = empfaenger

    part2 = MIMEText(html, "html")
    message.attach(part2)

    bot.send_mail('IHK Lehrstellenbörse Abruf', message, sendermail, empfaenger)

    time.sleep(delay)
