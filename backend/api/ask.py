from http.server import BaseHTTPRequestHandler
import json
import os
import requests

class handler(BaseHTTPRequestHandler):
from http.server import BaseHTTPRequestHandler
import json
import os
import re

class handler(BaseHTTPRequestHandler):
    def get_comprehensive_legal_response(self, question):
        """Get comprehensive legal response based on Pakistani law"""
        question_lower = question.lower()
        
        # Comprehensive Pakistani Legal Knowledge Base
        legal_responses = {
            # Criminal Law
            'murder': {
                'answer': """**Murder Laws in Pakistan**

**Legal Framework:**
• **Pakistan Penal Code (PPC) 1860** - Sections 300-304
• **Code of Criminal Procedure (CrPC) 1898** - Investigation procedures
• **Qisas and Diyat Ordinance 1990** - Islamic criminal law provisions

**Definition of Murder (Section 300 PPC):**
• **Intentional killing** with knowledge that act is likely to cause death
• **Act done with intention** of causing bodily injury likely to cause death
• **Act done with knowledge** that it is so imminently dangerous that it must cause death

**Types of Murder:**
• **Qatl-e-Amd** (Intentional murder) - Punishable by death or life imprisonment
• **Qatl-e-Khata** (Unintentional murder) - Diyat (blood money) payable
• **Qatl-e-Shibh-e-Amd** (Semi-intentional) - Diyat and imprisonment

**Legal Procedures:**
1. **FIR Registration** - Report to nearest police station
2. **Investigation** - Police investigation under CrPC
3. **Charge Sheet** - Filed in Sessions Court
4. **Trial** - Before Sessions Judge
5. **Appeal** - High Court and Supreme Court

**Punishments:**
• **Death Penalty** - For Qatl-e-Amd (with victim's heirs consent)
• **Life Imprisonment** - Alternative to death penalty
• **Diyat** - Blood money as per Islamic law
• **Arsh** - Compensation for injuries

**Rights of Accused:**
• Right to legal representation
• Right to bail (except in heinous cases)
• Right to fair trial
• Right to appeal

**Important:** Murder cases require immediate legal assistance. Contact a criminal lawyer immediately.""",
                'sources': [
                    {'law_name': 'Pakistan Penal Code 1860', 'section': 'Sections 300-304', 'relevance_score': 0.95},
                    {'law_name': 'Qisas and Diyat Ordinance 1990', 'section': 'Islamic Criminal Law', 'relevance_score': 0.9}
                ],
                'confidence': 0.9
            },
            
            'fir': {
                'answer': """**FIR (First Information Report) Procedure in Pakistan**

**Legal Basis:**
• **Section 154 of CrPC 1898** - Registration of FIR
• **Police Order 2002** - Police procedures
• **Supreme Court Guidelines** - FIR registration rights

**What is FIR:**
• **First Information Report** - Initial complaint about cognizable offense
• **Legal Document** - Basis for criminal investigation
• **Mandatory Registration** - Police cannot refuse cognizable offenses

**FIR Registration Process:**
1. **Visit Police Station** - Go to relevant police station
2. **Oral/Written Complaint** - Provide details of incident
3. **Recording** - Police officer records information
4. **Reading Back** - FIR read back to complainant
5. **Signature** - Complainant signs the FIR
6. **Copy Provided** - Free copy given to complainant
7. **GD Entry** - Entry made in General Diary

**Required Information:**
• **Date, Time, Place** of incident
• **Names of Accused** (if known)
• **Details of Offense** committed
• **Witnesses** present
• **Evidence** available
• **Complainant Details** - Name, address, CNIC

**Types of Offenses:**
• **Cognizable** - Police can arrest without warrant (murder, theft, etc.)
• **Non-Cognizable** - Requires court permission (minor disputes)

**Rights of Complainant:**
• **Free Registration** - No fee for FIR
• **Free Copy** - Entitled to FIR copy
• **Refusal Remedy** - Can approach magistrate if police refuse
• **Investigation Updates** - Right to know progress

**If Police Refuse FIR:**
1. **Written Application** - Submit written complaint
2. **Senior Officer** - Approach SHO or DSP
3. **Magistrate** - File application under Section 22-A CrPC
4. **High Court** - Constitutional petition as last resort

**Important Documents:**
• **CNIC** of complainant
• **Medical Reports** (if applicable)
• **Evidence** - Photos, documents
• **Witness Details**

**Time Limit:**
• **No Time Limit** for registration
• **Immediate Registration** for cognizable offenses
• **Delay Explanation** may be required for old incidents

**Important:** FIR is your legal right. Police cannot refuse to register FIR for cognizable offenses.""",
                'sources': [
                    {'law_name': 'Code of Criminal Procedure 1898', 'section': 'Section 154', 'relevance_score': 0.95},
                    {'law_name': 'Police Order 2002', 'section': 'Police Procedures', 'relevance_score': 0.85}
                ],
                'confidence': 0.95
            },
            
            'criminal': {
                'answer': """**Criminal Law in Pakistan - Comprehensive Guide**

**Primary Legislation:**
• **Pakistan Penal Code (PPC) 1860** - Defines criminal offenses
• **Code of Criminal Procedure (CrPC) 1898** - Criminal procedures
• **Qisas and Diyat Ordinance 1990** - Islamic criminal law
• **Anti-Terrorism Act 1997** - Terrorism-related offenses

**Major Criminal Offenses:**

**Crimes Against Person:**
• **Murder (Qatl)** - Sections 300-304 PPC
• **Hurt (Jurh)** - Sections 319-337 PPC
• **Kidnapping** - Sections 359-369 PPC
• **Rape** - Section 375-376 PPC

**Crimes Against Property:**
• **Theft** - Sections 378-382 PPC
• **Robbery** - Sections 390-402 PPC
• **Criminal Breach of Trust** - Sections 405-409 PPC
• **Cheating** - Sections 415-420 PPC

**Criminal Procedure Steps:**
1. **FIR Registration** - Section 154 CrPC
2. **Investigation** - Sections 156-173 CrPC
3. **Charge Sheet** - Section 173 CrPC
4. **Trial** - Sections 225-265 CrPC
5. **Judgment** - Section 353-365 CrPC
6. **Appeal** - Sections 372-417 CrPC

**Court Hierarchy:**
• **Magistrate Courts** - Minor offenses
• **Sessions Courts** - Major crimes
• **High Courts** - Appeals and constitutional matters
• **Supreme Court** - Final appeals

**Rights of Accused:**
• **Right to Legal Aid** - Free legal assistance
• **Right to Bail** - Except in non-bailable offenses
• **Right to Fair Trial** - Due process
• **Right to Appeal** - Higher court review
• **Right to Remain Silent** - No self-incrimination

**Punishments:**
• **Death Penalty** - For murder and terrorism
• **Life Imprisonment** - 25 years imprisonment
• **Simple/Rigorous Imprisonment** - Various terms
• **Fine** - Monetary penalty
• **Diyat** - Blood money under Islamic law

**Bail Provisions:**
• **Bailable Offenses** - Bail as right
• **Non-Bailable Offenses** - Court discretion
• **Anticipatory Bail** - Pre-arrest protection
• **Post-Arrest Bail** - After arrest

**Important:** Criminal matters require immediate legal assistance. Contact a qualified criminal lawyer.""",
                'sources': [
                    {'law_name': 'Pakistan Penal Code 1860', 'section': 'Criminal Offenses', 'relevance_score': 0.95},
                    {'law_name': 'Code of Criminal Procedure 1898', 'section': 'Criminal Procedures', 'relevance_score': 0.9}
                ],
                'confidence': 0.9
            }
        }
        
        # Check for specific criminal law topics
        for keyword, response in legal_responses.items():
            if keyword in question_lower:
                return response
        
        # Check for other legal topics with pattern matching
        if any(word in question_lower for word in ['theft', 'robbery', 'stealing']):
            return {
                'answer': """**Theft and Robbery Laws in Pakistan**

**Theft (Sections 378-382 PPC):**
• **Definition** - Dishonestly taking movable property
• **Punishment** - Up to 3 years imprisonment or fine
• **Aggravated Theft** - Enhanced punishment for repeat offenses

**Robbery (Sections 390-402 PPC):**
• **Definition** - Theft with violence or threat
• **Punishment** - Up to 10 years imprisonment
• **Dacoity** - Robbery by 5 or more persons (life imprisonment)

**Legal Procedure:**
1. File FIR immediately
2. Police investigation
3. Recovery of stolen property
4. Trial in Magistrate/Sessions Court

**Important:** Report theft/robbery immediately to police.""",
                'sources': [{'law_name': 'Pakistan Penal Code 1860', 'section': 'Sections 378-402', 'relevance_score': 0.9}],
                'confidence': 0.85
            }
        
        if any(word in question_lower for word in ['bail', 'arrest', 'custody']):
            return {
                'answer': """**Bail and Arrest Laws in Pakistan**

**Arrest Procedures (CrPC 1898):**
• **With Warrant** - Court-issued warrant
• **Without Warrant** - For cognizable offenses
• **Rights During Arrest** - Inform grounds, legal representation

**Types of Bail:**
• **Ordinary Bail** - For bailable offenses
• **Anticipatory Bail** - Pre-arrest protection
• **Post-Arrest Bail** - After arrest in non-bailable cases

**Bail Conditions:**
• **Surety** - Personal/property guarantee
• **Attendance** - Court appearances
• **Restrictions** - Travel, contact limitations

**Non-Bailable Offenses:**
• Murder, terrorism, rape, kidnapping
• Court discretion for bail
• Strict conditions if granted

**Important:** Contact lawyer immediately if arrested or anticipating arrest.""",
                'sources': [{'law_name': 'Code of Criminal Procedure 1898', 'section': 'Arrest and Bail', 'relevance_score': 0.9}],
                'confidence': 0.85
            }
        
        # Default comprehensive response for unmatched queries
        return {
            'answer': f"""**Pakistani Legal Information**

**Your Question:** {question}

**Comprehensive Legal Assistance Available For:**

**Criminal Law:**
• Murder, theft, robbery, fraud cases
• FIR registration and procedures
• Bail applications and arrest matters
• Court procedures and appeals

**Family Law:**
• Marriage registration and requirements
• Divorce procedures (Talaq, Khula, Mubarat)
• Child custody and maintenance
• Inheritance and succession

**Property Law:**
• Property registration and transfer
• Land disputes and ownership
• Rent and tenancy matters
• Property documentation

**Constitutional Law:**
• Fundamental rights enforcement
• Constitutional petitions
• Government procedures
• Public interest litigation

**Corporate Law:**
• Company registration and compliance
• Business licensing
• Contract disputes
• Commercial litigation

**For Immediate Legal Help:**
• **Pakistan Bar Council:** +92-51-9201681
• **Legal Aid:** District court legal aid offices
• **Emergency Helplines:** 1099 (Punjab), 1092 (Sindh)

**Common Legal Resources:**
• Constitution of Pakistan 1973
• Pakistan Penal Code 1860
• Code of Criminal Procedure 1898
• Muslim Family Laws Ordinance 1961

**Next Steps:**
1. Specify your exact legal issue for detailed guidance
2. Gather relevant documents
3. Contact a qualified Pakistani lawyer
4. Consider legal aid if needed

**Important:** For specific legal advice and representation, always consult qualified Pakistani legal professionals.""",
            'sources': [{'law_name': 'Pakistani Legal System', 'section': 'Comprehensive Legal Information', 'relevance_score': 0.7}],
            'confidence': 0.7
        }
    
    def generate_sources(self, question):
        """Generate relevant legal sources based on question content"""
        question_lower = question.lower()
        sources = []
        
        # Constitutional matters
        if any(word in question_lower for word in ['constitution', 'fundamental rights', 'article', 'constitutional']):
            sources.append({
                'law_name': 'Constitution of Pakistan 1973',
                'section': 'Fundamental Rights & Constitutional Provisions',
                'relevance_score': 0.9
            })
        
        # Criminal law matters
        if any(word in question_lower for word in ['murder', 'theft', 'criminal', 'fir', 'police', 'arrest', 'bail']):
            sources.extend([
                {
                    'law_name': 'Pakistan Penal Code 1860',
                    'section': 'Criminal Offenses',
                    'relevance_score': 0.9
                },
                {
                    'law_name': 'Code of Criminal Procedure 1898',
                    'section': 'Criminal Procedures',
                    'relevance_score': 0.85
                }
            ])
        
        # Family law matters
        if any(word in question_lower for word in ['marriage', 'divorce', 'nikah', 'khula', 'mehr', 'family']):
            sources.append({
                'law_name': 'Muslim Family Laws Ordinance 1961',
                'section': 'Marriage & Divorce',
                'relevance_score': 0.9
            })
        
        # Property law matters
        if any(word in question_lower for word in ['property', 'land', 'ownership', 'transfer', 'registration']):
            sources.extend([
                {
                    'law_name': 'Transfer of Property Act 1882',
                    'section': 'Property Transfer',
                    'relevance_score': 0.9
                },
                {
                    'law_name': 'Registration Act 1908',
                    'section': 'Document Registration',
                    'relevance_score': 0.8
                }
            ])
        
        # Civil procedure matters
        if any(word in question_lower for word in ['civil', 'suit', 'court', 'procedure', 'litigation']):
            sources.append({
                'law_name': 'Civil Procedure Code 1908',
                'section': 'Civil Court Procedures',
                'relevance_score': 0.85
            })
        
        # Corporate/business law
        if any(word in question_lower for word in ['company', 'business', 'corporate', 'partnership']):
            sources.append({
                'law_name': 'Companies Act 2017',
                'section': 'Corporate Law',
                'relevance_score': 0.85
            })
        
        # Default sources if no specific match
        if not sources:
            sources.append({
                'law_name': 'Pakistani Legal System',
                'section': 'General Legal Information',
                'relevance_score': 0.7
            })
        
        return sources
    
    def generate_follow_up_questions(self, question):
        """Generate relevant follow-up questions based on the query"""
        question_lower = question.lower()
        
        # Criminal law follow-ups
        if any(word in question_lower for word in ['murder', 'criminal', 'fir', 'police', 'arrest']):
            return [
                "What is the procedure for filing an FIR?",
                "How to get bail in criminal cases?",
                "What are the rights of an accused person?"
            ]
        
        # Family law follow-ups
        if any(word in question_lower for word in ['marriage', 'divorce', 'nikah', 'khula']):
            return [
                "What documents are required for marriage registration?",
                "How to file for Khula in family court?",
                "What are the maintenance rights after divorce?"
            ]
        
        # Property law follow-ups
        if any(word in question_lower for word in ['property', 'land', 'ownership']):
            return [
                "How to verify property ownership?",
                "What is the property registration process?",
                "How to resolve property disputes?"
            ]
        
        # Constitutional law follow-ups
        if any(word in question_lower for word in ['constitution', 'rights', 'fundamental']):
            return [
                "How to file a constitutional petition?",
                "What are the limitations on fundamental rights?",
                "How to enforce constitutional rights?"
            ]
        
        # Default follow-ups
        return [
            "What legal procedures should I follow?",
            "What documents do I need for this matter?",
            "How can I find a qualified Pakistani lawyer?"
        ]

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
            
            # Get comprehensive legal response
            legal_info = self.get_comprehensive_legal_response(question)
            
            # Generate contextual follow-up questions
            follow_up_questions = self.generate_follow_up_questions(question)
            
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
                "answer": f"""**Service Error**

I apologize, but I encountered a technical error while processing your question: "{question if 'question' in locals() else 'your legal query'}"

**For Immediate Legal Assistance:**
• **Pakistan Bar Council:** +92-51-9201681
• **Legal Aid Helpline:** Contact your nearest district court
• **Emergency Legal Help:** 1099 (Punjab), 1092 (Sindh)

**Error Details:** {str(e)}

**Recommended Action:** Please contact a qualified Pakistani legal professional for immediate assistance with your legal matter.""",
                "sources": [],
                "confidence": 0.1,
                "follow_up_questions": [
                    "How can I contact Pakistan Bar Council?",
                    "Where is my nearest district court?",
                    "How to find legal aid services?"
                ]
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