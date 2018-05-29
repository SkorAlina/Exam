import xml.etree.ElementTree as ET
import sqlite3

conn = sqlite3.connect('trackdb.sqlite')
cur = conn.cursor()

# Make some fresh tables using executescript()
cur.executescript('''
DROP TABLE IF EXISTS Artist;
DROP TABLE IF EXISTS Genre;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Track;
CREATE TABLE Artist (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT UNIQUE
);
CREATE TABLE Genre(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    genre TEXT
);
CREATE TABLE Album (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    artist_id INTEGER,
    title TEXT UNIQUE
);
CREATE TABLE Track (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    title TEXT UNIQUE,
    album_id INTEGER,
    genre_id INTEGER,
    len INTEGER,
    rating INTEGER,
    count INTEGER
);
''')

fname = raw_input('Enter file name: ')
if (len(fname) < 1): fname = 'Library.xml'


# <key>Track ID</key><integer>369</integer>
# <key>Name</key><string>Another One Bites The Dust</string>
# <key>Artist</key><string>Queen</string>
def lookup(d, key):
    found = False
    for child in d:
        if found: return child.text
        if child.tag == 'key' and child.text == key:
            found = True
    return None


stuff = ET.parse(fname)
all = stuff.findall('dict/dict/dict')
print 'Dict count:', len(all)
for entry in all:
    if (lookup(entry, 'Track ID') is None): continue
    # 2 create a genre value
    name = lookup(entry, 'Name')
    artist = lookup(entry, 'Artist')
    album = lookup(entry, 'Album')
    count = lookup(entry, 'Play Count')
    rating = lookup(entry, 'Rating')
    length = lookup(entry, 'Total Time')
    genre = lookup(entry, 'Genre')
    # 3 check the genre value
    if any([genre is None, name is None, artist is None, album is None]):
        continue

    print name, artist, genre, album, count, rating, length

    cur.execute('''INSERT OR IGNORE INTO Artist (name) 
        VALUES ( ? )''', (artist,))
    cur.execute('SELECT id FROM Artist WHERE name = ? ', (artist,))
    artist_id = cur.fetchone()[0]

    # 4 insert the genre value into Genre table. Create a genre_id value

    cur.execute('''INSERT OR IGNORE INTO Genre(genre)
                VALUES ( ?)''', (genre,))
    cur.execute('SELECT id FROM Genre WHERE genre = ? ', (genre,))
    genre_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Album (title, artist_id) 
                VALUES ( ?, ? )''', (album, artist_id))
    cur.execute('SELECT id FROM Album WHERE title = ? ', (album,))
    album_id = cur.fetchone()[0]

    # 5 insert the genre_id value into Track table
    cur.execute('''INSERT OR REPLACE INTO Track
        (title, album_id, genre_id, len, rating, count)
        VALUES ( ?, ?, ?, ?, ?, ? )''',
                (name, album_id, genre_id, length, rating, count))
    conn.commit()


genreStr = 'SELECT genre FROM Genre'
temp = [i[0] for i in cur.execute(genreStr)]
unic = {u for u in temp}
data_dict = {x: temp.count(x) for x in unic}
sorted_val = sorted(data_dict.items(), key=operator.itemgetter(1))
for val in sorted_val[::-1]:
    print val[0], val[1]

cur.close()
conn.close()