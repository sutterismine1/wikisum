import discord  #discord api wrapper
import aiohttp  #non-blocking web scraper
import bs4 #beautifulsoup (used for html parsing)
token = open('token.txt').read()
swears = open('swears.txt').readlines() #profanity to help mark articles NSFW
client = discord.Client()
@client.event
async def on_message(message):
    if client.user.mentioned_in(message):   #if bot is mentioned
            if not message.mention_everyone:    #if someone says @everyone or @here it will not respond
                await message.channel.send("Hi there buddy, I am WikiSum. Say `wikihelp`for more information!")
    if message.content == 'wikihelp':   #help command
        helpembed = discord.Embed(title="Commands", description="You have summoned me. Here are the available commands.", color=0xFF0000)
        helpembed.add_field(name= 'wikisum {article}', value= 'Searches for an article to summarize.')
        helpembed.add_field(name= 'wikidis {name}', value = 'Searches for a disambiguation page.')
        helpembed.add_field(name= 'wikisearch {name}', value = 'Displays the search results for a query.')
        helpembed.add_field(name= 'wikisupport', value='Links to the support server')
        helpembed.add_field(name= 'wikiinvite', value='Generates bot invite link.')
        await message.channel.send(embed=helpembed)
    if message.content == 'wikisupport':    #support command
        if message.guild.id != 582349055993315330:  #if user isn't already in the support server
            await message.channel.send('Go to this channel to report any bugs or suggestions.\nhttps://discord.gg/nRxJ4HD')
        else:
            await message.channel.send('Go to <#643924090469744670> for help, or to <#644183940097376287> to suggest something :smile:')
    if message.content == 'wikiinvite':
        await message.channel.send('Go to this channel to report any bugs or suggestions.\nhttps://discord.gg/nRxJ4HD')
    if message.content.startswith('wikisum '):  #main command. It summarizes wiki articles
        msg = message.content.replace('wikisum ', '')   #finds what name the user requested
        usablemsg = msg.replace(' ', '_')   #wiki url format replaces spaces with _
        async with aiohttp.ClientSession() as session:  #starts a aiohttp session (acts as a asyncronous requests module)
            async with session.get('https://en.wikipedia.org/wiki/' + usablemsg) as r:
                if r.status == 200:
                    text = await r.read()
                    soup = bs4.BeautifulSoup(text, features="lxml")
                    if 'may refer to:' in soup.get_text():
                        await message.channel.send("I'm sorry but this title can refer to multiple entries.")
                        articles = []
                        for entry in soup.find_all('a'):
                            article = entry.get('title')
                            if article != None and msg.lower() != article.lower():
                                if msg.lower() in article.lower() and 'Edit' not in article and 'wiktionary:' not in article and 'Special:' not in article and ' – ' not in article and 'disambiguation' not in article and article not in articles:
                                    articles.append(article)
                        disembed = discord.Embed(title='Disambiguation')
                        articles = str(articles).replace('[', '').replace(']', '')
                        src = str(r.url)
                        src = src.replace(')', '\)')
                        disembed.add_field(name='Articles', value=f'The available articles are: `{articles}`\nTaken from: [{src}]({src})')
                        await message.channel.send(embed=disembed)
                    elif '(Redirected from' in soup.get_text():
                        sumembed = discord.Embed(title=msg)
                        await message.channel.send(f"This is a redirect to the article: `{soup.h1.text}`. The summary may be inaccurate.")
                        for t in soup.find_all('p'):
                            if t.text.strip() != '' and t.parent.name == 'div':
                                src = str(r.url)
                                src = src.replace(')', '\)')
                                sumembed.add_field(name='Summary: ', value= t.text + '\n' + 'Taken from: ' + f'[{src}]({src})')
                                await message.channel.send(embed=sumembed)
                            else:
                                continue
                            break
                    else:
                        sumembed = discord.Embed(title=msg)
                        for t in soup.find_all('p'):
                            if t.text.strip() != '' and t.parent.name == 'div':
                                src = str(r.url)
                                src = src.replace(')', '\)')
                                for swear in swears:
                                    if swear.strip().lower() in t.text.lower():
                                        await message.channel.send('Warning: The following article is not safe for work. (Profane words and sexual topics.)')
                                        sumembed.add_field(name='Summary: ', value= '||' + t.text + '||' + '\n' + 'Taken from: ' + f'[{src}]({src})')
                                        await message.channel.send(embed=sumembed)
                                        return
                                sumembed.add_field(name='Summary: ', value= t.text + '\n' + 'Taken from: ' + f'[{src}]({src})')
                                await message.channel.send(embed=sumembed)
                            else:
                                continue
                            break
                else:
                    await message.channel.send('This article does not exist. :person_shrugging:\nTry using `wikisearch` to search for the article.')
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
                        article = entry.get('title')
                        if article != None and msg.lower() != article.lower():
                            if msg.lower() in article.lower() and 'Edit' not in article and 'wiktionary:' not in article and 'Special:' not in article and ' – ' not in article and 'disambiguation' not in article:
                                articles.append(article)
                    disembed = discord.Embed(title=f'Disambiguation of {msg}')
                    strarticles = str(articles).replace('[', '').replace(']', '')
                    src = str(r.url).replace(')', '\)')
                    print(len(articles))
                    fieldcount = len(articles) // 20
                    print(fieldcount)
                    if fieldcount == 2:
                        half = len(articles) // 2
                        articles1 = articles[:half]
                        articles2 = articles[half:]
                        disembed.add_field(name='Articles 1', value=f'The available articles are: `{articles1}`')
                        disembed.add_field(name='Articles 2', value=f'More available articles are: `{articles2}`\nTaken from: [{src}]({src})')
                        await message.channel.send(embed=disembed)
                        return
                    elif fieldcount <=4:
                        quarter = len(articles) // 4
                        articles1 = articles[:quarter]
                        articles2 = articles[quarter:quarter + quarter]
                        articles3 = articles[quarter + quarter:quarter + quarter + quarter]
                        articles4 = articles[quarter + quarter + quarter:]
                        disembed.add_field(name='Articles 1', value=f'The available articles are: `{articles1}`')
                        disembed.add_field(name='Articles 2', value=f'More available articles are: `{articles2}`')
                        disembed.add_field(name='Articles 3', value=f'More available articles are: `{articles3}`')
                        disembed.add_field(name='Articles 4', value=f'More available articles are: `{articles4}`\nTaken from: [{src}]({src})')
                        await message.channel.send(embed=disembed)
                    else:
                        try:
                            disembed.add_field(name='Articles', value=f'The available articles are: `{strarticles}`\nTaken from: [{src}]({src})')
                            await message.channel.send(embed=disembed)
                        except:
                            await message.channel.send('The amount of links is way to large. Try using wikisearch instead.')
                else:
                    await message.channel.send('This article does not exist. :person_shrugging:\nTry using `wikisearch` to search for the article.')
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
                        count= 0
                        for entry in soup.find_all('li'):
                            count += 1
                            checkresult = entry.get('class')
                            if str(checkresult) == "['mw-search-result']":
                                result = entry.div.a
                                result = result.get('title')
                                results.append(str(count - 4) + '. ' + result)
                        results = '\n'.join(results)
                        resembed = discord.Embed(title=msg)
                        resembed.add_field(name='Search Results:', value=results)
                        await message.channel.send(embed=resembed)
client.run(token)
