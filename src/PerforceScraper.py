from __future__ import division, print_function
import P4
from pprint import pprint
import datetime
import os.path
from collections import defaultdict
from pymongo import MongoClient
from pymongo.operations import ReplaceOne


class PerforceScraper(object):
    def __init__(self, p4, client):
        self.p4 = p4
        self.client = client
    def run(self, path):
        return self._parse_perforce_path(path)
    
    def save_into_db(self, files):
        for file in files:
            pprint(file)
#         replacements = [ReplaceOne({
#             _id:
#         })]
        self.client.Hackathon.files.insert_many(files)
    
    def _parse_perforce_path(self, path):
        try:
            files = self.p4.run('files', path + '/*')
        except:
            files = []
        
        dirs = self.p4.run('dirs', path + '/*') 
        
        file_objects = []   
        if len(files) == 0 and len(dirs) == 0:
            try:
                file = self.p4.run('files', path)[0]
                return self._create_file_object(file['depotFile'], file['time'])
            except:
                None
        
        for file in files:
            if file['action'] not in ['delete', 'move/delete']:
                file_objects.append(self._parse_perforce_path(file['depotFile']))
        
        subdir_objects = []
        for dir in dirs:
            subdir_objects.append(self._parse_perforce_path(dir['dir']))
        
        current_dir_object = self._create_current_dir_object(path, file_objects, subdir_objects)
        # just combine everything and save into database
        file_objects.append(current_dir_object)
        if len(file_objects) > 0:
            pass
            #self.save_into_db(file_objects)
        return current_dir_object
        
    def _create_file_object(self, file, time):
        filelog = self.p4.run_filelog(file)
        revisions = filelog[0].revisions

        file_object = {'_id': file,
                       'name': os.path.split(file)[1],
                       'size': revisions[0].fileSize,
                       'creator': revisions[-1].user,
                       'contributors': self._get_file_contributors(revisions),
                       'latest_rev_date': time
                      }
        
        return file_object
    
    def _create_current_dir_object(self, full_path, file_objects, subdir_objects):
        current_dir_object = {'_id': full_path,
                              'name': os.path.split(full_path)[1],
                              'contributors': self._get_dir_contributors(file_objects, subdir_objects)
                             }
        
        return current_dir_object
                             
    def _get_file_contributors(self, revisions):
        users = defaultdict(int)
        oldest = len(revisions) * .9
        
        for index, revision in enumerate(revisions):
            if index >= oldest:
                users[revision.user] += 6 
            else:
                points = self._get_revision_weight(revision)
                users[revision.user] += points
        return [{'user': k, 'points': v} for k, v in users.items()]
            
    def _get_dir_contributors(self, file_objects, subdir_objects):
        users = defaultdict(int)
        for file in file_objects:
            for contrib in file['contributors']:
                users[contrib['user']] += contrib['points']
        for directory in subdir_objects:
            for contrib in directory['contributors']:
                users[contrib['user']] += contrib['points']

        return [{'user': k, 'points': v} for k, v in users.items()]

    def _get_revision_weight(self, revision):
        current_date = datetime.datetime.now()
        revision_date = revision.time
        time_difference = current_date - revision_date
        days_ago = time_difference.days
        
        if days_ago <= 30:
            return 5
        elif 31 <= days_ago <= 90:
            return 4
        elif 91 <= days_ago <= 180:
            return 3
        elif 181 <= days_ago <= 365:
            return 2
        else:
            return 1
        
        
def main():
    p4 = P4.P4()
    p4.connect()
    db = MongoClient('172.22.117.118')
    scraper = PerforceScraper(p4, db)
    output = scraper.run('//package/PackageTools/PackageReleaseSite')
    
    if 'creator' in output:
        print('Creator: ', output.get('creator', ''))
    contrib = sorted(output['contributors'], cmp=lambda x, y: x['points'] - y['points'], reverse=True)
    print('Top Contributors:')
    for item in contrib:
        print('\t', item['user'])

if __name__ == "__main__":
    main()
    