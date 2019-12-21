import discord, aiohttp, bs4
token = open('token.txt').read()
client = discord.Client()
@client.event
async def on_message(message):
    if client.user.mentioned_in(message):
            if not message.mention_everyone:    #if someone says @everyone or @here it will not respond
                await message.channel.send("Hi there buddy, I am WikiSum. Say `wikihelp`for more information!")
    if message.content == 'wikihelp':
        helpembed = discord.Embed(title="Commands", description="You have summoned me. Here are the available commands.", color=0xFF0000)
        helpembed.add_field(name= 'wikisum {article}', value= 'Searches for an article to summarize.')
        helpembed.add_field(name= 'wikidis {name}', value = 'Searches for a disambiguation page.')
        helpembed.add_field(name= 'wikisearch {name}', value = 'Displays the search results for a query.')
        helpembed.add_field(name= 'wikisupport', value='Links to the support server')
        helpembed.add_field(name= 'wikiinvite', value='Generates bot invite link.')
        await message.channel.send(embed=helpembed)
    if message.content.startswith('wikisum '):
        msg = message.content.replace('wikisum ', '')
        usablemsg = msg.replace(' ', '_')
        async with aiohttp.ClientSession() as session:
            async with session.get('https://en.wikipedia.org/wiki/' + usablemsg) as r:
                if r.status == 200:
                    text = await r.read()
                    soup = bs4.BeautifulSoup(text, features="lxml")
                    if 'may refer to:' in soup.get_text():
                        await message.channel.send("I'm sorry but this title can refer to multiple entries.")
                        articles = []
                        for entry in soup.find_all('a'):
                            test = entry.get('title')
                            if test != None and msg.lower() != test.lower():
                                if msg.lower() in test.lower() and 'Edit' not in test and 'wiktionary:' not in test and 'Special:' not in test and ' – ' not in test and 'disambiguation' not in test and test not in articles:
                                    articles.append(test)
                        await message.channel.send(f'The available articles are: `{str(articles)}`')
                    elif '(Redirected from' in soup.get_text():
                        await message.channel.send(f'This is a redirect to the article: `{soup.h1.text}`. The summary may be inaccurate.')
                        await message.channel.send('------------------------------------------------')
                        for t in soup.find_all('p'):
                            if t.text.strip() != '' and t.parent.name == 'div':
                                await message.channel.send(t.text)
                            else:
                                continue
                            break
                    else:
                        for t in soup.find_all('p'):
                            if t.text.strip() != '' and t.parent.name == 'div':
                                await message.channel.send(t.text)
                            else:
                                continue
                            break
                else:
                    await message.channel.send('This article does not exist. :person_shrugging:')
    if message.content.startswith('wikidis '):
        msg = message.content.replace('wikidis ', '')
        usablemsg = msg.replace(' ', '_')
        async with aiohttp.ClientSession() as session:
            async with session.get('https://en.wikipedia.org/wiki/' + usablemsg + '_(disambiguation)') as r:
                if r.status == 200:
                    text = await r.read()
                    soup = bs4.BeautifulSoup(text, features="lxml")
                    articles = []
                    for entry in soup.find_all('a'):
                        test = entry.get('title')
                        if test != None and msg.lower() != test.lower():
                            if msg.lower() in test.lower() and 'Edit' not in test and 'wiktionary:' not in test and 'Special:' not in test and ' – ' not in test and 'disambiguation' not in test:
                                articles.append(test)
                    await message.channel.send(f'The available articles are: `{str(articles)}`')
                else:
                    await message.channel.send('This article does not exist. :person_shrugging:')
    if message.content.startswith('wikisearch '):
        msg = message.content.replace('wikisearch ', '')
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://en.wikipedia.org/w/index.php?sort=relevance&search={msg}&title=Special:Search&profile=advanced&fulltext=1&advancedSearch-current=%7B%7D&ns0=1') as r:
                if r.status == 200:
                    text = await r.read()
                    soup = bs4.BeautifulSoup(text, features="lxml")
                    if 'There were no results matching the query.' in soup.get_text():
                        await message.channel.send('There were no results matching the query.')
                    else:
                        results = []
                        for entry in soup.find_all('li'):
                            checkresult = entry.get('class')
                            if str(checkresult) == "['mw-search-result']":
                                result = entry.div.a
                                result = result.get('title')
                                results.append('-' + result)
                        results = '\n'.join(results)
                        await message.channel.send(str(results))
client.run(token)
