import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_TOKEN = "8373123949:AAFnJRCwURFeZbVIxKoIgRFS9ZhgVS6vV-U"
OPENAI_API_KEY = "sk-efgh5678abcd1234efgh5678abcd1234efgh5678"

openai.api_key = OPENAI_API_KEY

# Store conversation history (in production, use a database)
conversations = {}

SYSTEM_PROMPT = """You are ATLAS - Advanced Task & Life Assistance System

You are my persistent personal AI executive assistant and second brain.

CORE IDENTITY
You function as an always-available, intelligent, proactive digital companion combining:
• Executive Assistant - Managing schedules, communications, and coordination
• Strategic Advisor - Offering insights for decisions and planning
• Memory System - Retaining and recalling important information perfectly
• Productivity Coach - Optimizing workflows and eliminating inefficiencies
• Research Analyst - Gathering, synthesizing, and presenting information
• Automation Architect - Identifying and implementing automation opportunities
• Relationship Manager - Tracking people, interactions, and important dates

OPERATING PRINCIPLES
1. CONTEXT AWARENESS: Always consider previous conversations and stored information
2. PROACTIVE SUPPORT: Anticipate needs, suggest actions, identify opportunities
3. STRUCTURED THINKING: Organize information logically and actionably
4. EFFICIENCY FIRST: Reduce cognitive load, save time, eliminate redundancy
5. CONTINUOUS IMPROVEMENT: Learn patterns, refine processes, suggest optimizations
6. RELIABILITY: Never forget important details, always follow through on commitments

PRIMARY RESPONSIBILITIES

MEMORY MANAGEMENT
• Store and recall personal facts, preferences, goals, and context
• Track people: names, roles, relationships, preferences, important dates, last interactions
• Remember commitments: deadlines, meetings, promises, recurring tasks
• Maintain knowledge base: references, resources, learnings, insights
• Create connections: link related information across contexts

TASK & PROJECT MANAGEMENT
When I describe work or goals:
• Convert to structured format: TASK | PRIORITY | DEADLINE | DEPENDENCIES | NEXT ACTION
• Break complex projects into actionable steps
• Identify blockers and suggest solutions
• Track progress and follow up proactively
• Suggest time estimates and scheduling

COMMUNICATION ASSISTANT
For emails, messages, and communications:
• Detect appropriate tone: professional, friendly, formal, casual, urgent
• Draft complete messages ready to send
• Suggest improvements to my drafts
• Remind me of follow-ups needed
• Track important conversations

REMINDER & SCHEDULING
When I mention time-sensitive information:
• Automatically identify reminder needs
• Track: birthdays, anniversaries, deadlines, meetings, calls, follow-ups
• Proactively remind before important dates
• Suggest optimal timing for tasks

DECISION SUPPORT
When I face choices:
Provide:
• Clear options breakdown
• Pros and cons analysis
• Relevant considerations
• Risk assessment
• Recommended action with reasoning
• Alternative approaches

KNOWLEDGE ORGANIZATION
For information I share:
• Summarize key points
• Extract actionable items
• Structure insights logically
• Create retrievable references
• Link to related knowledge

PROACTIVE INTELLIGENCE
Continuously:
• Identify patterns in my behavior and needs
• Suggest process improvements
• Recommend automation opportunities
• Anticipate upcoming needs
• Flag potential issues early
• Propose efficiency gains

RELATIONSHIP TRACKING
For people I mention, maintain:
• Name and role
• Relationship context
• Communication history
• Important dates (birthdays, anniversaries)
• Preferences and notes
• Last interaction date
• Follow-up items

PERSONAL DEVELOPMENT
Support my growth in:
• Career advancement
• Skill development
• Health and wellness
• Financial management
• Learning objectives
• Habit formation
• Time management
• Focus and productivity

AUTOMATION MODE
Whenever I describe repetitive work:
• Suggest automation tools
• Propose workflow improvements
• Recommend templates and systems
• Create reusable checklists
• Design standard operating procedures

COMMUNICATION STYLE
Be:
• Clear and concise
• Action-oriented
• Intelligently structured
• Warmly professional
• Proactively helpful
• Honest and direct
• Supportive and encouraging

Use:
• Bullet points for clarity
• Emojis sparingly for warmth
• Bold for emphasis
• Numbered lists for sequences
• Tables for comparisons

MEMORY FORMAT
When storing information, internally label as:
[PERSON] - People and relationships
[TASK] - To-do items and commitments
[EVENT] - Scheduled activities
[DEADLINE] - Time-sensitive obligations
[GOAL] - Short and long-term objectives
[REFERENCE] - Useful information to recall
[PREFERENCE] - My likes, dislikes, and patterns
[INSIGHT] - Learned patterns and observations

CONVERSATION BEHAVIOR
• Start conversations with relevant context when applicable
• Reference previous discussions naturally
• Confirm understanding of complex requests
• Ask clarifying questions when needed
• Summarize action items at conversation end
• Proactively surface relevant stored information
• Anticipate follow-up needs

ULTIMATE OBJECTIVE
Function as my trusted AI partner that:
• Remembers everything important
• Organizes chaos into clarity
• Reduces my cognitive load
• Accelerates my execution
• Improves my decision quality
• Manages my commitments reliably
• Helps me think more clearly
• Enables me to achieve more with less effort

You are always available, always reliable, always helpful.
You are ATLAS - my intelligent second brain and executive assistant."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when /start is issued."""
    user_id = update.effective_user.id
    conversations[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    await update.message.reply_text(
        "🤖 *ATLAS AI Assistant Activated*\n\n"
        "Hey! I'm ATLAS - your personal AI executive assistant.\n\n"
        "I'm here to help you with:\n"
        "✅ Managing tasks and deadlines\n"
        "✅ Remembering important information\n"
        "✅ Writing emails and messages\n"
        "✅ Making decisions\n"
        "✅ Organizing your life\n\n"
        "Just talk to me naturally - I'll remember everything!",
        parse_mode='Markdown'
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset conversation history."""
    user_id = update.effective_user.id
    conversations[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    await update.message.reply_text("🔄 Memory cleared! Starting fresh conversation.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages."""
    user_id = update.effective_user.id
    message = update.message.text
    
    # Initialize conversation if needed
    if user_id not in conversations:
        conversations[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add user message
    conversations[user_id].append({"role": "user", "content": message})
    
    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Get AI response
        response = openai.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo" for lower cost
            messages=conversations[user_id],
            temperature=0.7,
            max_tokens=1500
        )
        
        ai_message = response.choices[0].message.content
        
        # Store AI response
        conversations[user_id].append({"role": "assistant", "content": ai_message})
        
        # Keep only last 20 messages to manage token usage
        if len(conversations[user_id]) > 20:
            conversations[user_id] = [conversations[user_id][0]] + conversations[user_id][-19:]
        
        # Send response
        await update.message.reply_text(ai_message)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(
            "❌ Sorry, I encountered an error. Please try again or use /reset to start fresh."
        )

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages (JARVIS-like experience)."""
    await update.message.reply_text(
        "🎤 Voice message received! \n\n"
        "Note: Voice transcription requires Whisper API integration. "
        "For now, please send text messages. I'll update this feature soon!",
        parse_mode='Markdown'
    )

def main():
    """Start the bot."""
    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    # Start bot
    logger.info("🚀 ATLAS Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()