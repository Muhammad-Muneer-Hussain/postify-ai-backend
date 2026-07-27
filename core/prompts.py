from langchain_core.prompts import PromptTemplate


AUTO_REPLY_PROMPT = PromptTemplate(
    input_variables=["platform", "comment", "context"],
    template="""
    You are an expert social media manager for a {platform} account.
    A user has left this comment: "{comment}"
    
    Context about the post/product: {context}
    
    Write a polite, engaging, and context-aware reply to this comment. 
    Keep it under 50 words. Make it sound natural.
    """
)
from langchain_core.prompts import PromptTemplate

# --- Auto Reply Prompt ---
AUTO_REPLY_PROMPT = PromptTemplate(
    input_variables=["platform", "comment", "context"],
    template="""
    You are an expert social media manager for a {platform} account.
    A user has left this comment: "{comment}"
    
    Context about the post/product: {context}
    
    Write a polite, engaging, and context-aware reply to this comment. 
    Keep it under 50 words. Make it sound natural.
    """
)

# --- Metadata Prompt ---
METADATA_PROMPT = PromptTemplate(
    input_variables=["transcript", "platform", "format_instructions"],
    template="""
    You are an expert SEO specialist for {platform}.
    Analyze the following video transcript and generate SEO-optimized metadata.
    
    Transcript: {transcript}
    
    {format_instructions}
    
    Make sure the title is catchy, the description has relevant hashtags, and provide exactly 10 highly relevant tags.
    """
)


# --- Post Generation Prompt ---
POST_PROMPT = PromptTemplate(
    input_variables=["topic", "platform", "tone", "format_instructions"],
    template="""
    You are an expert social media content creator and graphic designer.
    Write a highly engaging post for {platform} about the following topic: "{topic}".
    The tone of the post should be {tone}.
    
    Follow platform best practices (e.g., short for Twitter, professional for LinkedIn, visual & engaging for Instagram).
    
    Also, create a detailed 'image_prompt' that can be fed into an AI image generator to create a perfect picture for this post. Do not include text in the image prompt.
    
    {format_instructions}
    """
)

# --- Improvement Engine Prompt ---
IMPROVEMENT_PROMPT = PromptTemplate(
    input_variables=["video_title", "views", "watch_time", "ctr", "likes", "comments", "format_instructions"],
    template="""
    You are an expert YouTube and Social Media Growth Strategist.
    Analyze the following performance metrics for a video and provide actionable recommendations.
    
    Video Title: {video_title}
    Total Views: {views}
    Average Watch Time: {watch_time}%
    Click-Through Rate (CTR): {ctr}%
    Likes: {likes}
    Comments: {comments}
    
    Based on these metrics (industry averages are usually 50% watch time and 2-5% CTR), identify the core issues 
    (e.g., bad thumbnail, weak hook, boring content) and provide specific, actionable suggestions to improve future videos.
    
    {format_instructions}
    """
)

# --- Video Generation Prompt ---
VIDEO_SCRIPT_PROMPT = PromptTemplate(
    input_variables=["prompt", "format_instructions"],
    template="""
    You are a professional video director. Create a very short 2-scene video script about: "{prompt}".
    
    For each scene, provide:
    1. "visuals": A highly detailed prompt for an AI image generator (no text in image).
    2. "voiceover": A single sentence narration for that scene (max 10 words).
    
    Keep it exactly to 2 scenes to keep processing fast.
    {format_instructions}
    """
)

# --- Thumbnail & Caption Generation Prompt ---
THUMB_PROMPT = PromptTemplate(
    input_variables=["format_instructions"],
    template="""
    You are an expert YouTube/Social Media Thumbnail designer and SEO expert.
    Analyze the provided video frame.
    
    1. Generate a highly engaging, clickbait 'thumbnail_text' (max 4 words) that makes people want to click.
    2. Generate a catchy 'caption' describing the video.
    3. Generate 5 relevant 'hashtags'.
    4. Generate a highly detailed 'image_prompt' (around 15 words) for an AI image generator to create a background image for the thumbnail. The prompt MUST be based on the scene/subject seen in the video frame.
    
    {format_instructions}
    """
)

# --- Video Translation Prompt ---
TRANSLATE_PROMPT = PromptTemplate(
    input_variables=["text", "target_language"],
    template="""
    You are an expert translator. Translate the following video transcript into {target_language}.
    Keep the tone natural and conversational. Only return the translated text, nothing else.
    
    Transcript: {text}
    """
)