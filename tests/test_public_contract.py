import hashlib,io,json,sqlite3,sys,tempfile,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from bootstrap_tools import safe_members,configure_mesh_export
from check_public import validate_catalogue
from catalog import SCHEMA
from ink_paths import iter_paths
from text_index import fnv,leaves

class PublicContract(unittest.TestCase):
    def test_catalogue_contract(self):
        data=json.loads((ROOT/'docs/catalogue.json').read_text(encoding='utf-8'))
        self.assertEqual(validate_catalogue(data),[])
        self.assertEqual(len(data['findings']),34)
        for f in data['findings']:
            self.assertEqual(f['id'],'NCA-'+hashlib.sha256(f['slug'].encode()).hexdigest()[:12].upper())
            self.assertGreaterEqual(len(f['assets']),2)
            self.assertTrue(f['details']['support']);self.assertTrue(f['details']['sql'])
    def test_asset_payload_rejected(self):
        d=json.loads((ROOT/'docs/catalogue.json').read_text(encoding='utf-8'));d['findings'][0]['assets'][0]['audio_base64']='excluded'
        self.assertIn('Unexpected asset payload fields',validate_catalogue(d))
    def test_path_hash_is_canonical(self):
        self.assertEqual(fnv('base/Example.mesh'),fnv('BASE\\example.mesh'))
        self.assertEqual(fnv('base\\quest\\minor_quests\\mq009\\scenes\\mq009_01_hook.scene'),'12894907652176725168')
    def test_reference_parser_preserves_named_and_numeric_paths(self):
        obj={'image':{'DepotPath':{'$value':'base\\example.xbm'}},'children':[{'DepotPath':{'$value':'12345'}}]}
        self.assertEqual(iter_paths(obj),[('base\\example.xbm','image',0),('12345','children',0)])
    def test_text_pointer_escaping(self):
        self.assertEqual(list(leaves({'a/b~c':'example'})),[('/a~1b~0c','example')])
    def test_sqlite_trigram_chinese_search(self):
        db=sqlite3.connect(':memory:');db.executescript(SCHEMA)
        db.execute("INSERT INTO text_search(doc_id,text) VALUES(1,'這是夜之城的測試')")
        self.assertEqual(db.execute('SELECT doc_id FROM text_search WHERE text_search MATCH ?',('"夜之城"',)).fetchone()[0],1)
        db.close()
    def test_zip_traversal_rejected(self):
        data=io.BytesIO()
        with zipfile.ZipFile(data,'w') as z:z.writestr('../escape','x')
        data.seek(0)
        with tempfile.TemporaryDirectory() as folder,zipfile.ZipFile(data) as z:
            with self.assertRaises(ValueError):safe_members(z,Path(folder))
    def test_upstream_bom_settings(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'appsettings.json';p.write_text('{"Logging":{"LogLevel":{"Default":"Information"}}}',encoding='utf-8-sig')
            configure_mesh_export(p);d=json.loads(p.read_text(encoding='utf-8'))
            self.assertFalse(d['MeshExportArgs']['withMaterials'])
            self.assertEqual(d['Logging']['LogLevel']['Default'],'Information')
    def test_release_has_local_web_dependencies(self):
        html=(ROOT/'docs/index.html').read_text(encoding='utf-8')
        self.assertNotIn('src="http',html)
        self.assertNotIn('127.0.0.1:18779',html)
        self.assertTrue((ROOT/'web/vendor/three-LICENSE.txt').is_file())

if __name__=='__main__':unittest.main()
