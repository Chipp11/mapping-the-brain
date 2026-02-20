#!/bin/bash
# Quick semantic search against your Cognee knowledge graph
# Usage: bash cognee-chunks.sh "query text" [top_k]

QUERY="${1:?Usage: cognee-chunks.sh 'query' [top_k]}"
TOP_K="${2:-3}"

# Activate your Cognee virtual environment
source "${COGNEE_VENV:-$HOME/.cognee-venv}/bin/activate" 2>/dev/null

python3 -c "
import cognee, asyncio
from cognee.modules.search.types.SearchType import SearchType

async def search():
    results = await cognee.search(
        '${QUERY}',
        query_type=SearchType.CHUNKS,
        top_k=${TOP_K}
    )
    for r in results:
        text = r.get('text', '')
        print(text[:300])
        print('---')

asyncio.run(search())
"
