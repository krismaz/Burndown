using LiteDB;

var dbFile = @"C:\Users\krise\AppData\Roaming\Playnite\library\categories.db";
var dbFile2 = @"C:\Users\krise\AppData\Roaming\Playnite\library\games.db";
Guid category = Guid.Empty;


using (var db = new LiteDatabase($"Filename={dbFile};Mode=Exclusive;Journal=false"))
{ 
    db.GetCollectionNames().ToList().ForEach(name =>
    {
            var collection = db.GetCollection(name);

            var documents = collection.FindAll().ToList();
            foreach ( var document in documents)
            {
                if (document["Name"] == "Backlog")
                {
                    category = document["_id"].AsGuid;
                }
            }

    });
}


using (var db = new LiteDatabase($"Filename={dbFile2};Mode=Exclusive;Journal=false"))
{
    db.GetCollectionNames().ToList().ForEach(name =>
    {
        var collection = db.GetCollection(name);

        var documents = collection.FindAll().ToList();
        foreach (var document in documents)
        {
            if (document.ContainsKey("CategoryIds") && document["CategoryIds"].AsArray.Contains(category))
            {
                Console.WriteLine(document["_id"].AsGuid.ToString());
            }
        }
    });
}

