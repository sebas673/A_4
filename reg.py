import SocketServer, SimpleHTTPServer, requests, sqlite3, sys

class Reply(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def do_GET(self):
    # Page to send back.
    Page = """<!DOCTYPE html>
<html>

<html>
<title>W3.CSS</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
<body style="background-color:powderblue;">

<div class="w3-container w3-teal">
  <h1>Assignment 4</h1>
</div>
  
  <div class="w3-display-container w3-powderblue" style="height:500px;">

    <form action="" method="get">
    Search: <input type="text" name="search" placeholder="dep[/num]"><br>
    <button type="submit">Search</button><br>
    <button type="submit" formaction="@">Count</button><br>
    <button type="submit" formaction="%">Clear</button><br>
    </form>
</div>



</body>
</html>"""


    # at the homepage
    if len(self.path) == 1:
      self.send_response(200)
      self.send_header("Content-Type", "text/html")
      self.send_header("Content-Length", str(len(Page)))
      self.end_headers()
      self.wfile.write(Page)

    # showing results
    else:
      searchNeeded = True
      countNeeded = False
      countAll = False
      clearNeeded = False
      clearAll = False
      str_code = ''
      sql_count_course = """SELECT * FROM counts WHERE dept = '"""
      counter = 0
      found = False

      # connects to db
      connection = sqlite3.connect("reg.db")
      c = connection.cursor()

      # splits up URL
      url = self.path[1:].split("/", 1)
      if len(url) == 2:
        if url[0] == 'count':
          countNeeded = True
          searchNeeded = False
        elif url[0] == 'clear':
          clearNeeded = True
          searchNeeded = False
        else:
          if len(url[0]) < 3:
            searchNeeded = False
          if len(url[1]) < 3:
            searchNeeded = False
        needsClassNumber = True
      else:
        needsClassNumber = False
        if url[0] == 'count':
          countAll = True
          searchNeeded = False
        elif url[0] == 'clear':
          clearAll = True
          searchNeeded = False

      # html URL
      # search needed
      if self.path[1] == '?':
        url = self.path[7:].split("=", 1)
        url = url[1].split("%2F", 1)
        if len(url) == 1:
          url[0] = url[0]
          needsClassNumber = False
        else:
          url[1] = url[1]
          if len(url[0]) < 3:
            searchNeeded = False
          if len(url[1]) < 3:
            searchNeeded = False
          needsClassNumber = True

      # count needed
      elif self.path[1] == '@':
        url = self.path[8:].split("=", 1)
        if url[1] != '':
          countNeeded = True
          searchNeeded = False
        else:
          countAll = True
          searchNeeded = False

      #clear needed
      elif self.path[1] == '%':
        url = self.path[8:].split("=", 1)
        if url[1] != '':
          clearNeeded = True
          searchNeeded = False
        else:
          clearAll = True
          searchNeeded = False

      # searches for course and title
      if searchNeeded:

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        # self.wfile.write("<html><body>")

        # updates db with query
        command = "SELECT * FROM counts WHERE dept = '" + url[0].lower() + "';"
        c.execute(command)
        num = c.fetchall()

        if len(num) != 0 and len(url[0]) == 3:
          command = "UPDATE counts SET counter = counter + 1 WHERE dept = '" + url[0].lower() + "';"
          c.execute(command)
          connection.commit()
        elif len(num) == 0 and len(url[0]) == 3:
          command = "INSERT INTO counts VALUES('" + url[0].lower() + "', 1);"
          # print insert
          c.execute(command)
          connection.commit()

        for term in all['term']:
          for subjects in term['subjects']:
            for code in subjects['code']:
              str_code = str_code + code
              counter += 1
              if counter == 3:
                if str_code.lower() == url[0].lower():
                  for courses in subjects['courses']:
                    if not needsClassNumber:
                      if len(courses['catalog_number']) > 2:
                        self.wfile.write("%s  %s  %s\n" % (str_code, courses['catalog_number'], courses['title']))
                        # self.wfile.write('<p style="font-family:courier;"> ' + str_code + '\t' + courses['catalog_number'] + '\t' + courses['title'] + "\n" + "<p>")

                        found = True
                    elif needsClassNumber:
                      if courses['catalog_number'] == url[1].upper():
                        self.wfile.write("%s  %s  %s\n" % (str_code, courses['catalog_number'], courses['title']))
                        # self.wfile.write('<p style="font-family:courier;"> ' + str_code + '\t' + courses['catalog_number'] + '\t' + courses['title'] + "\n" + "<p>")
                        found = True
                else:
                  counter = 0
                  str_code = ''
        # self.wfile.write("<body><html>")

      # code for number of searches for a specific course
      elif countNeeded:

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        # self.wfile.write("<html><body>")

        if len(url[1]) == 3:
          command = sql_count_course + url[1].lower() + "';"""
          c.execute(command)
          data = c.fetchall()
          if len(data) != 0:
            self.wfile.write("%s  %s\n" % (data[0][0].upper(), data[0][1]))
            # self.wfile.write('<p style="font-family:courier;"> ' + str(data[0][0].upper()) + '\t' + str(data[0][1]) + "\n" + "<p>")
          else:
            self.wfile.write("%s  %s\n" % (url[1].upper(), 0))
            # self.wfile.write('<p style="font-family:courier;"> ' + url[1].upper() + '\t' + "0" + "\n" + "<p>")
        # self.wfile.write("<body><html>")

      # returns number of searches for all courses
      elif countAll:
        # print "count all"
        c.execute("SELECT * FROM counts;")
        data = c.fetchall()

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        # self.wfile.write("<html><body>")

        for i in data:
          if i[1] != 0: # remove this is need to print all the zero entries
            self.wfile.write("%s  %s\n" % (i[0].upper(), i[1]))
            # self.wfile.write('<p style="font-family:courier;"> '+ i[0].upper() + '\t'+ str(i[1]) + "\n" + "<p>")
        # self.wfile.write("<body><html>")

      # clears all of db
      elif clearAll:
        c.execute("DELETE FROM counts;")
        for term in all['term']:
          for subjects in term['subjects']:
            for code in subjects['code']:
              str_code = str_code + code
              counter += 1
              if counter == 3:
                command = "INSERT INTO counts VALUES('" + str_code.lower() + "', 0);"
                c.execute(command)
                counter = 0
                str_code = ""
        connection.commit()

        # will just stay on the same page
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write("Cleared all entries")

      # needs yo clear a course count
      elif clearNeeded:
        command = "UPDATE counts SET counter = 0 WHERE dept = '" + url[1].lower() + "';"
        c.execute(command)
        connection.commit()

        # will just stay on the same page
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write("Cleared entries for " + str(url[1].upper()))


      # no matching courses or numbers
      elif not found:
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('\n')


#----------------------------------------------------------------------------------------------------------------------

all = []


def get_OIT(url):
  r = requests.get(url)
  if r.status_code != 200:
    return ["bad json"]
  return r.json()

def main():
  global all
  firstTime = True

  # connect to db
  connection = sqlite3.connect("reg.db")
  c = connection.cursor()

  # Read OIT feed before starting the server.
  oit = 'http://etcweb.princeton.edu/webfeeds/courseofferings/?fmt=json&term=current&subject=all'
  all = get_OIT(oit)

  # insert all the courses into db with 0 searches
  str_code = ""
  counter = 0
  for term in all['term']:
    for subjects in term['subjects']:
      for code in subjects['code']:
        str_code = str_code + code
        counter += 1
        if counter == 3:
          if firstTime:
            c.execute("SELECT * FROM counts WHERE dept = 'aas';")
            data = c.fetchall()
          if len(data) == 0:
            command = "INSERT INTO counts VALUES('" + str_code.lower() + "', 0);"
            c.execute(command)
            counter = 0
            str_code = ""
            firstTime = False
  connection.commit()
  connection.close()

  print("server is listening on $port")
  SocketServer.ForkingTCPServer(('', int(sys.argv[1])), Reply).serve_forever()

main()
