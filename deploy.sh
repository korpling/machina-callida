x=$(git tag --points-at HEAD)
echo "export const version = '${x}';" > mc_frontend/src/version.ts
docker-compose build
docker-compose down
docker-compose up -d
