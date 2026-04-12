from http.server import BaseHTTPRequestHandler
import json
import os
import re

class handler(BaseHTTPRequestHandler):
    def get_legal_response(self, question):
        """Generate specific legal responses based on question content"""
        question_lower = question.lower()
        
        # Legal knowledge base
        legal_knowledge = {
            'fundamental rights': {
                'answer': """**Fundamental Rights in Pakistan Constitution**

**Articles 8-28** of the Constitution of Pakistan 1973 guarantee fundamental rights:

**Key Fundamental Rights:**
• **Right to Life (Article 9)** - Protection of life and liberty
• **Right to Dignity (Article 14)** - Dignity of man and privacy of home
• **Freedom of Movement (Article 15)** - Freedom to move and reside
• **Freedom of Assembly (Article 16)** - Peaceful assembly without arms
• **Freedom of Association (Article 17)** - Form associations and unions
• **Freedom of Trade (Article 18)** - Practice any profession or trade
• **Freedom of Speech (Article 19)** - Freedom of speech and expression
• **Freedom of Religion (Article 20)** - Practice and propagate religion
• **Right to Education (Article 25A)** - Free and compulsory education
• **Right to Information (Article 19A)** - Access to information
• **Equality Before Law (Article 25)** - Equal protection of law

**Important:** These rights are subject to reasonable restrictions as provided by law.""",
                'sources': [{'law_name': 'Constitution of Pakistan 1973', 'section': 'Articles 8-28', 'relevance_score': 0.95}],
                'confidence': 0.9
            },
            
            'act 45': {
                'answer': """**About Act 45 in Pakistani Law**

**Possible References:**
• **Companies Act 2017 (Act No. XVII of 2017)** - Section 45 deals with company registration
• **Pakistan Penal Code 1860** - Section 45 defines "life" in legal context
• **Code of Criminal Procedure 1898** - Section 45 relates to arrest procedures

**For Act 45 specifically, you may be referring to:**
• **The Specific Relief Act 1877** - Contains provisions about legal remedies
• **Various provincial acts** numbered 45 in different years

**To get accurate information:**
• Specify the full name of the act
• Mention the year of enactment
• Contact Pakistan Bar Council: +92-51-9201681

**Common Legal Acts in Pakistan:**
• Constitution of Pakistan 1973
• Pakistan Penal Code 1860
• Companies Act 2017
• Contract Act 1872""",
                'sources': [{'law_name': 'Pakistani Legal System', 'section': 'Various Acts', 'relevance_score': 0.8}],
                'confidence': 0.7
            },
            
            'marriage': {
                'answer': """**Marriage Laws in Pakistan**

**Key Legislation:**
• **Muslim Family Laws Ordinance 1961**
• **Family Courts Act 1964**
• **West Pakistan Family Courts Rules 1965**

**Marriage Requirements:**
• **Nikah** - Islamic marriage contract
• **Registration** - Marriage registration with Union Council
• **Witnesses** - Two adult Muslim witnesses required
• **Mehr** - Dower amount specified in Nikah

**Legal Procedures:**
• Marriage registration within specified time
• Nikah Registrar appointment
• Marriage certificate issuance

**For Non-Muslims:**
• **Christian Marriage Act 1872**
• **Parsi Marriage and Divorce Act 1936**
• **Hindu Marriage Act** (in some provinces)

**Important:** Consult family law experts for specific marriage legal matters.""",
                'sources': [{'law_name': 'Muslim Family Laws Ordinance 1961', 'section': 'Marriage Provisions', 'relevance_score': 0.9}],
                'confidence': 0.85
            },
            
            'divorce': {
                'answer': """**Divorce Laws in Pakistan**

**Islamic Divorce Types:**
• **Talaq** - Divorce by husband
• **Khula** - Divorce sought by wife
• **Mubarat** - Mutual consent divorce
• **Faskh** - Dissolution by court

**Legal Requirements:**
• **90-day waiting period** (Iddat) for reconciliation
• **Union Council notification** mandatory
• **Arbitration Council** formation for reconciliation
• **Maintenance** during Iddat period

**Court Procedures:**
• File petition in Family Court
• Mediation attempts required
• Evidence and witness examination
• Final decree issuance

**Women's Rights:**
• Right to seek Khula
• Maintenance during Iddat
• Child custody rights (Hizanat)
• Recovery of Mehr amount

**Important:** Family law matters require specialized legal counsel.""",
                'sources': [{'law_name': 'Muslim Family Laws Ordinance 1961', 'section': 'Divorce Provisions', 'relevance_score': 0.9}],
                'confidence': 0.85
            },
            
            'property': {
                'answer': """**Property Laws in Pakistan**

**Key Legislation:**
• **Transfer of Property Act 1882**
• **Registration Act 1908**
• **Land Revenue Act 1967**
• **Stamp Act 1899**

**Property Rights:**
• **Ownership** - Absolute ownership rights
• **Transfer** - Sale, gift, inheritance
• **Registration** - Mandatory for immovable property
• **Mutation** - Revenue record updates

**Legal Procedures:**
• **Sale Deed** registration with Sub-Registrar
• **Stamp Duty** payment as per law
• **NOC** from relevant authorities
• **Mutation** in revenue records

**Islamic Inheritance:**
• **Sharia Law** governs Muslim inheritance
• **Fixed shares** for heirs as per Quran
• **Succession Act 1925** for non-Muslims

**Important:** Property transactions require thorough legal verification.""",
                'sources': [{'law_name': 'Transfer of Property Act 1882', 'section': 'Property Transfer', 'relevance_score': 0.9}],
                'confidence': 0.85
            }
        }
        
        # Check for specific topics
        for topic, info in legal_knowledge.items():
            if any(keyword in question_lower for keyword in topic.split()):
                return info
        
        # Check for specific patterns
        if re.search(r'\bact\s+\d+\b', question_lower):
            return legal_knowledge['act 45']
        
        # Default response for unmatched questions
        return {
            'answer': f"""**Pakistani Legal Information**

**Your Question:** {question}

**General Guidance:** I can help with common Pakistani legal topics including:

• **Constitutional Law** - Fundamental rights, government structure
• **Family Law** - Marriage, divorce, inheritance
• **Property Law** - Ownership, transfer, registration
• **Criminal Law** - Pakistan Penal Code provisions
• **Corporate Law** - Company formation and regulations

**For Specific Legal Advice:**
• **Pakistan Bar Council:** +92-51-9201681
• **Local District Court:** Visit your nearest court
• **Qualified Lawyer:** Consult a Pakistani legal professional

**Common Legal Resources:**
• Constitution of Pakistan 1973
• Pakistan Penal Code (PPC) 1860
• Code of Criminal Procedure (CrPC) 1898
• Muslim Family Laws Ordinance 1961

**Try asking about:** "fundamental rights", "marriage laws", "property transfer", "divorce procedures", etc.""",
            'sources': [{'law_name': 'Pakistani Legal System', 'section': 'General Information', 'relevance_score': 0.7}],
            'confidence': 0.6
        }

    def do_POST(self):
        try:
            # Parse request
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                body = json.loads(post_data.decode('utf-8'))
                question = body.get('question', '').strip()
            else:
                question = ""
            
            if not question:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'detail': 'Question cannot be empty'}).encode())
                return
            
            # Get specific legal response
            legal_info = self.get_legal_response(question)
            
            # Generate follow-up questions based on topic
            follow_up_questions = [
                "What are the legal procedures for this matter?",
                "How can I find a qualified Pakistani lawyer?",
                "What documents are needed for this legal issue?"
            ]
            
            # Topic-specific follow-ups
            question_lower = question.lower()
            if 'fundamental rights' in question_lower or 'constitution' in question_lower:
                follow_up_questions = [
                    "What are the limitations on fundamental rights?",
                    "How can fundamental rights be enforced?",
                    "What is the procedure for constitutional petitions?"
                ]
            elif 'marriage' in question_lower:
                follow_up_questions = [
                    "What documents are required for marriage registration?",
                    "What are the legal requirements for Nikah?",
                    "How to register marriage with Union Council?"
                ]
            elif 'divorce' in question_lower:
                follow_up_questions = [
                    "What is the procedure for Khula?",
                    "How long is the Iddat period?",
                    "What are women's rights in divorce?"
                ]
            elif 'property' in question_lower:
                follow_up_questions = [
                    "What is the property registration process?",
                    "How to verify property ownership?",
                    "What are the stamp duty rates?"
                ]
            
            result = {
                "answer": legal_info['answer'],
                "sources": legal_info['sources'],
                "confidence": legal_info['confidence'],
                "follow_up_questions": follow_up_questions
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            error_response = {
                "answer": f"I apologize, but I encountered an error: {str(e)}. For legal assistance, contact Pakistan Bar Council: +92-51-9201681",
                "sources": [],
                "confidence": 0.1,
                "follow_up_questions": ["How can I contact Pakistan Bar Council?"]
            }
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()