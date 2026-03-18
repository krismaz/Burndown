user_query = """
query {
  Viewer {
    id
    name
  }
}"""

media_query = """query ($userId: Int, $page:Int) {
  Page (page: $page) {
    pageInfo {
      hasNextPage
      currentPage
    }
  mediaList  (userId: $userId, status: PLANNING) {
    id
    media {
      id
      title {
        romaji
      }
      type
      status
      duration
      episodes
      volumes
      siteUrl
    }
  }
}
}"""