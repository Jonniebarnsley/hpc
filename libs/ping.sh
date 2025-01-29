#!/bin/bash

message=$1
message=${message:=Ping!}
discord_url=https://discord.com/api/webhooks/1334194162991370391/1rJ6t6WqLH8QXEpJzzfyp3kKZ69EQQ7ZJUPoG-H0b3UJ1R8RRPjcBYLVIAyA59dTGtB3

curl -H "Content-Type: application/json" -X POST -d "{\"content\": \"$message\"}" $discord_url

