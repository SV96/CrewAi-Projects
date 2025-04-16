#!/usr/bin/env python
import asyncio
from random import randint
from typing import List
from pydantic import BaseModel
from crewai.flow import Flow, listen, start
from writeabook.types import Chapter, ChapterOutline

from writeabook.crews.outline_book_crew.outline_crew import OutlineCrew
from writeabook.crews.write_book_chapter_crew.write_book_chapter_crew import WriteBookChapterCrew


class BookState(BaseModel):
    title:str = (
        "The Current state of AI in Match 2025 - Trends across Industires."
    )
    book:List[Chapter] = []
    book_outline: List[ChapterOutline] = []
    topic:str=(
        "Exploring the latest trends in AI across different industires as of March 2025."
    )
    goal:str=(
        """
        As of March 2025, artificial intelligence (AI) stands at the forefront of technological innovation, profoundly influencing 
        various sectors and redefining the boundaries of what's possible. This book aims to provide developers—both seasoned professionals 
        and newcomers—with a comprehensive overview of the current state of AI.​
        We will explore the latest trends shaping industries, analyze significant advancements, and discuss potential future developments. 
        From the emergence of autonomous AI agents capable of complex decision-making to breakthroughs in multimodal models that process 
        and generate diverse data types, the AI landscape is rapidly evolving. Notably, tools like OpenAI's "Operator" assistant and Anthropic's 
        voice-enabled Claude AI exemplify the strides made in creating more interactive and versatile AI systems.​
        Furthermore, the integration of AI in defense, as seen with startups like Scout AI developing robotic armies, and the application 
        of AI in optimizing supply chains and enhancing workplace productivity, highlight the expansive reach of AI technologies.​
        This book is designed to inform and equip developers with insights into cutting-edge AI technologies, preparing them for 
        the innovations that lie ahead in this dynamic field.​
    """)


class BookFlow(Flow[BookState]):

    @start()
    def generate_book_outline(self):
        output = (
            OutlineCrew()
            .crew()
            .kickoff(inputs={"topic":self.state.topic,"goal":self.state.goal})
        )
        chapters = output["chapters"]
        self.state.book_outline = chapters

    @listen(generate_book_outline)
    async def write_chapters(self):
        print("Writing Book Chapters")
        tasks = []

        async def write_single_chapter(chapter_outline):
            output = (
                WriteBookChapterCrew()
                .crew()
                .kickoff(
                    inputs={
                        "goal": self.state.goal,
                        "topic": self.state.topic,
                        "chapter_title": chapter_outline.title,
                        "chapter_description": chapter_outline.description,
                        "book_outline": [
                            chapter_outline.model_dump_json()
                            for chapter_outline in self.state.book_outline
                        ],
                    }
                )
            )
            title = output["title"]
            content = output["content"]
            chapter = Chapter(title=title, content=content)
            return chapter

        for chapter_outline in self.state.book_outline:
            print(f"Writing Chapter: {chapter_outline.title}")
            print(f"Description: {chapter_outline.description}")
            # Schedule each chapter writing task
            task = asyncio.create_task(write_single_chapter(chapter_outline))
            tasks.append(task)

        # Await all chapter writing tasks concurrently
        chapters = await asyncio.gather(*tasks)
        print("Newly generated chapters:", chapters)
        self.state.book.extend(chapters)

        print("Book Chapters", self.state.book)
            
            

    @listen(write_chapters)
    async def join_and_save_chapter(self):
        book_content = ""
        
        for chapter in self.state.book:
            book_content += f"# {chapter.title} \n\n"
            book_content += f"# {chapter.content} \n\n"
        
        book_title = self.state.title    
        
        filename = f"./{book_title.replace(' ','_')}.md"
        
        with open(filename,"w",encoding="utf-8") as file:
            file.write(book_content)


def kickoff():
    write_flow = BookFlow()
    write_flow.kickoff()


def plot():
    write_flow = BookFlow()
    write_flow.plot()


if __name__ == "__main__":
    kickoff()
