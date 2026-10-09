/** SQLite scene transport. Source validation belongs to scene-file.js.
 * Imports never modify the database; export creates a new scene-only snapshot.
 */
export const MAX_ARCHIVE_BYTES=4*1024*1024;
export const MAX_SOURCE_BYTES=1024*1024;
const HEADER='SQLite format 3\0';
const DDL_SCHEMA='CREATE TABLE skin_scene_schema (version INTEGER NOT NULL)';
const DDL_SCENE='CREATE TABLE skin_scenes (id INTEGER PRIMARY KEY, record_version INTEGER NOT NULL, source_json TEXT NOT NULL)';
function source(text){if(typeof text!=='string'||new TextEncoder().encode(text).length>MAX_SOURCE_BYTES)throw Error('Scene source exceeds 1 MiB or is not text');return text;}
function table(db,name,ddl){const rows=db.exec('SELECT type,sql FROM sqlite_master WHERE name=?',[name])[0]?.values;if(rows?.length!==1||rows[0][0]!=='table'||rows[0][1].replace(/\s+/g,' ').trim().toLowerCase()!==ddl.toLowerCase())throw Error('This SQLite project does not contain a supported posing scene');}
export async function createSceneArchive({SQL}={}){
 if(!SQL){if(typeof globalThis.initSqlJs!=='function')throw Error('SQLite file support is unavailable');SQL=await globalThis.initSqlJs({locateFile:()=>new URL('./vendor/sqljs/sql-wasm.wasm',import.meta.url).href});}
 return Object.freeze({
  encode(text){source(text);const db=new SQL.Database();try{db.run('BEGIN');db.run(DDL_SCHEMA);db.run(DDL_SCENE);db.run('INSERT INTO skin_scene_schema VALUES (1)');db.run('INSERT INTO skin_scenes VALUES (1,1,?)',[text]);db.run('COMMIT');const bytes=db.export();if(bytes.length>MAX_ARCHIVE_BYTES)throw Error('Scene archive exceeds 4 MiB');return bytes;}finally{db.close();}},
  decode(input){const bytes=input instanceof Uint8Array?input:input instanceof ArrayBuffer?new Uint8Array(input):null;if(!bytes||bytes.byteLength<100||bytes.byteLength>MAX_ARCHIVE_BYTES)throw Error('Scene file must be a SQLite file up to 4 MiB');if(String.fromCharCode(...bytes.subarray(0,16))!==HEADER)throw Error('Open a .human.sqlite scene file');let db;try{db=new SQL.Database(new Uint8Array(bytes));db.run('PRAGMA query_only=ON');table(db,'skin_scene_schema',DDL_SCHEMA);const schema=db.exec('SELECT version FROM skin_scene_schema LIMIT 2')[0]?.values;if(schema?.length!==1||schema[0][0]!==1)throw Error('Unsupported scene database version; expected 1');table(db,'skin_scenes',DDL_SCENE);const metadata=db.exec('SELECT id,record_version,length(CAST(source_json AS BLOB)),typeof(source_json) FROM skin_scenes LIMIT 2')[0]?.values;if(metadata?.length!==1||metadata[0][0]!==1)throw Error('Scene file must contain exactly one scene');if(metadata[0][1]!==1)throw Error('Unsupported scene record version; expected 1');if(metadata[0][3]!=='text'||metadata[0][2]>MAX_SOURCE_BYTES)throw Error('Scene source exceeds 1 MiB or is not text');return source(db.exec('SELECT source_json FROM skin_scenes WHERE id=1')[0].values[0][0]);}catch(error){throw Error('Cannot open scene: '+(error.message||String(error)));}finally{db?.close();}}
 });
}
