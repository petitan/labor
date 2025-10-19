% ===============================================================================
% PeTitan Kft. ISO 17025:2018 Minőségirányítási Kézikönyv Dokumentumosztály
% petitanmk.cls
% ===============================================================================
%
% Dokumentumosztály PeTitan Kft. kalibrálólaboratórium ISO 17025:2018 szerinti
% minőségirányítási dokumentumaihoz.
%
% Szerző: Claude AI (Anthropic)
% Dátum: 2025.01.15
% Verzió: 1.0
%
% Használat:
%   \documentclass[options]{petitanmk}
%
% Opciók:
%   main     - Fő minőségirányítási kézikönyv (alapértelmezett)
%   chapter  - Fejezet dokumentum
%   appendix - Melléklet dokumentum
%   procedure - Eljárás dokumentum
%   standalone - Önálló kalibrálási eljárás (document_type)
%
% v2.2.3 (Issue #3) - Document mode options:
%   standalone - Standalone PDF mode (default, document_mode)
%   embedded   - Embedded appendix mode with numeric appendix numbering
%
% ===============================================================================

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{petitanmk}[2025/01/15 v1.0 PeTitan ISO 17025 Document Class]

% ===== DUMMY COMMANDS (for docjl compatibility) =====
% These commands are defined by docjl templates but must exist for compilation
\newcommand{\petitandoctype}[1]{}  % Dokumentum típus - ignoráljuk
\newcommand{\CompanyName}[1]{}     % Cég név - ignoráljuk
\newcommand{\CompanyAddress}[1]{}  % Cég cím - ignoráljuk
\newcommand{\CompanyTaxNumber}[1]{}  % Adószám - ignoráljuk

% ===== ALAPÉRTELMEZETT OPCIÓK =====
% Document type flags
\newif\if@petitan@main\@petitan@maintrue
\newif\if@petitan@chapter\@petitan@chapterfalse
\newif\if@petitan@appendix\@petitan@appendixfalse
\newif\if@petitan@procedure\@petitan@procedurefalse
\newif\if@petitan@standalone\@petitan@standalonefalse

% v2.2.3 (Issue #3) - Document mode flags
\newif\if@petitan@embedded\@petitan@embeddedfalse

% ===== DOKUMENTUM TÍPUS OPCIÓK =====
\DeclareOption{main}{%
    \@petitan@maintrue
    \@petitan@chapterfalse
    \@petitan@appendixfalse
    \@petitan@procedurefalse
    \@petitan@standalonefalse
}

\DeclareOption{chapter}{%
    \@petitan@mainfalse
    \@petitan@chaptertrue
    \@petitan@appendixfalse
    \@petitan@procedurefalse
    \@petitan@standalonefalse
}

\DeclareOption{appendix}{%
    \@petitan@mainfalse
    \@petitan@chapterfalse
    \@petitan@appendixtrue
    \@petitan@procedurefalse
    \@petitan@standalonefalse
}

\DeclareOption{procedure}{%
    \@petitan@mainfalse
    \@petitan@chapterfalse
    \@petitan@appendixfalse
    \@petitan@proceduretrue
    \@petitan@standalonefalse
}

\DeclareOption{standalone}{%
    \@petitan@mainfalse
    \@petitan@chapterfalse
    \@petitan@appendixfalse
    \@petitan@procedurefalse
    \@petitan@standalonetrue
}

% v2.2.3 (Issue #3) - Document mode option
\DeclareOption{embedded}{%
    \@petitan@embeddedtrue
}

% ===== ALAPÉRTELMEZETT OPCIÓK ÁTADÁSA =====
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{report}}
\ProcessOptions\relax

% ===== ALAPDOKUMENTUM OSZTÁLY BETÖLTÉSE =====
% v2.2.3 (Issue #3) - Changed default font size from 12pt to 11pt
\if@petitan@standalone
    \LoadClass[11pt,a4paper]{article}
\else
    \LoadClass[11pt,a4paper,twoside,openright]{report}
\fi

% ===== KÖTELEZŐ CSOMAGOK =====
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage[magyar]{babel}

% v2.2.3 (Issue #3) - Palatino font family
\RequirePackage{mathpazo}  % Palatino for text and math
\RequirePackage[scaled=0.95]{helvet}  % Helvetica for sans-serif
\RequirePackage{courier}  % Courier for monospace

% Geometria beállítások
\RequirePackage[margin=2.5cm]{geometry}
\setlength{\headheight}{15pt}

% ===== FORMÁZÁSI CSOMAGOK =====
\RequirePackage{fancyhdr}
\RequirePackage{lastpage}
\RequirePackage{titlesec}
\RequirePackage{tocloft}
\RequirePackage{hyperref}
\RequirePackage{xcolor}
\RequirePackage{graphicx}
\RequirePackage{enumitem}
\RequirePackage{multicol}

% ===== TÁBLÁZAT CSOMAGOK =====
\RequirePackage{booktabs}
\RequirePackage{tabularx}
\RequirePackage{array}
\RequirePackage{multirow}
\RequirePackage{longtable}
\RequirePackage{float}

% ===== MATEMATIKA ÉS MÉRTÉKEGYSÉGEK =====
\RequirePackage{amsmath}
\RequirePackage{amssymb}
\RequirePackage{siunitx}
\sisetup{
    output-decimal-marker = {,},
    group-separator = {\,},
    per-mode = symbol
}

% ===== TIKZ SZERVEZETI ÁBRÁKHOZ =====
\RequirePackage{tikz}
\usetikzlibrary{shapes, arrows, positioning, shadows}

% ===== TÖRDELÉS JAVÍTÁSA =====
\RequirePackage[protrusion=true,expansion=false]{microtype}
\tolerance=1000
\emergencystretch=3em

% ===== DOBOZOK ÉS KIEMELÉSEK =====
\RequirePackage[most]{tcolorbox}

% ===== PETITAN SZÍNEK =====
\definecolor{petitanblue}{RGB}{0,102,204}
\definecolor{petitangray}{RGB}{102,102,102}
\definecolor{petitangreen}{RGB}{0,153,51}
\definecolor{petitanred}{RGB}{204,0,51}
\definecolor{petitanorange}{RGB}{255,153,0}
\definecolor{petitanpurple}{RGB}{153,51,153}
\definecolor{petitanyellow}{RGB}{255,204,0}

% ===== ISO 17025 INFO BOX STÍLUSOK (v2.2.4 - Issue #4) =====

% nahinfo - Információs doboz (kék)
\newtcolorbox{nahinfo}[1][]{
    colback=blue!5!white,
    colframe=blue!75!black,
    fonttitle=\bfseries,
    title={#1}
}

% nahalert - Figyelmeztető doboz (piros)
\newtcolorbox{nahalert}[1][]{
    colback=red!5!white,
    colframe=red!75!black,
    fonttitle=\bfseries,
    title={#1}
}

% nahreq - Követelmény doboz (zöld)
\newtcolorbox{nahreq}[1][]{
    colback=green!5!white,
    colframe=green!75!black,
    fonttitle=\bfseries,
    title={#1}
}

% nahsec - Biztonsági doboz (sárga)
\newtcolorbox{nahsec}[1][]{
    colback=yellow!5!white,
    colframe=yellow!75!black,
    fonttitle=\bfseries,
    title={#1}
}

% nahvalid - Validációs doboz (lila)
\newtcolorbox{nahvalid}[1][]{
    colback=purple!5!white,
    colframe=purple!75!black,
    fonttitle=\bfseries,
    title={#1}
}

% ===== CÉGADAT MAKRÓK =====
\newcommand{\petitan}{PeTitan Kft.}
\newcommand{\petitanlab}{PeTitan Kft. Kalibrálólaboratórium}
\newcommand{\petitancim}{6727 Szeged, Algyői u. 19/A}
\newcommand{\petitanadoszam}{24696371-2-06}
\newcommand{\petitantel}{+36 62 499 212}
\newcommand{\petitanemail}{petitan@petitan.hu}

% ===== INTELLIGENS CÉGADAT BLOKKOK =====

% Hivatalos dokumentumok cégadat blokk
\newcommand{\CompanyOfficialBlock}{%
    \begin{tcolorbox}[colback=blue!5,colframe=blue!50,title={\textbf{Cégadatok}}]
    \textbf{Cégnév:} \petitan \\
    \textbf{Cím:} \petitancim \\
    \textbf{Adószám:} \petitanadoszam \\
    \textbf{Telefon:} \petitantel \\
    \textbf{E-mail:} \petitanemail
    \end{tcolorbox}
}

% Fejléc cégadat blokk appendix címekhez
\newcommand{\CompanyHeaderBlock}[1]{%
    \begin{center}
    \textbf{\petitanlab}\\
    \textbf{ISO/IEC 17025:2018 szerinti QMS}\\
    #1
    \end{center}
}

% Kapcsolattartási cégadat blokk kalibrálási bizonyítványokhoz
\newcommand{\CompanyContactBlock}{%
    \noindent
    \textbf{Laboratórium:} \petitanlab \\
    \textbf{Cím:} \petitancim \\
    \textbf{Kapcsolat:} \petitantel, \petitanemail
}

% Kompakt cégadat blokk dokumentum láblécekhez
\newcommand{\CompanyFooterBlock}{%
    \petitan -- \petitancim -- Tel.: \petitantel
}

% Egyszerű cégadat sor
\newcommand{\CompanySimpleLine}{%
    \petitan, \petitancim, \petitantel
}

% ===== KONTEXTUS-ÉRZÉKENY CÉGADAT MEGJELENÍTÉS =====

% Kalibrálási bizonyítvány fejléc
\newcommand{\CalibrationCertificateHeader}[2]{%
    \begin{center}
    \textbf{\Large \petitanlab}\\
    \vspace{0.2cm}
    \textbf{KALIBRÁLÁSI BIZONYÍTVÁNY}\\
    \textbf{Certificate No.: #1}\\
    \vspace{0.2cm}
    \textit{#2}
    \end{center}
    \CompanyContactBlock
    \vspace{0.5cm}
}

% Eljárás dokumentum fejléc
\newcommand{\ProcedureHeader}[3]{%
    \CompanyHeaderBlock{#1}
    \vspace{0.5cm}
    \begin{center}
    \textbf{\Large #2}\\
    \textbf{Eljárás kódja: #3}
    \end{center}
    \vspace{0.5cm}
}

% Minőségirányítási dokumentum fejléc
\newcommand{\QMSDocumentHeader}[2]{%
    \CompanyHeaderBlock{ISO/IEC 17025:2018 MINŐSÉGIRÁNYÍTÁSI RENDSZER}
    \vspace{0.5cm}
    \begin{center}
    \textbf{\LARGE #1}\\
    \textbf{Dokumentum kódja: #2}
    \end{center}
    \vspace{0.5cm}
}

% Automatikus lábléc beállítás dokumentumtípus alapján
\newcommand{\SetContextualFooter}[1]{%
    \if\relax\detokenize{#1}\relax
        % Ha nincs paraméter, alapértelmezett
        \fancyfoot[C]{\CompanyFooterBlock}
    \else
        \ifnum\pdfstrcmp{#1}{calibration}=0
            \fancyfoot[C]{\petitanlab\ -- Akkreditált kalibrálólaboratórium}
        \else\ifnum\pdfstrcmp{#1}{procedure}=0
            \fancyfoot[C]{\petitan\ -- Kalibrálási eljárás -- \thepage}
        \else\ifnum\pdfstrcmp{#1}{qms}=0
            \fancyfoot[C]{\petitan\ -- QMS dokumentum -- \thepage}
        \else
            \fancyfoot[C]{\CompanyFooterBlock}
        \fi\fi\fi
    \fi
}

% Intelligens cégadat beszúrás kontextus alapján
\newcommand{\InsertCompanyData}[1]{%
    \ifnum\pdfstrcmp{#1}{official}=0
        \CompanyOfficialBlock
    \else\ifnum\pdfstrcmp{#1}{contact}=0
        \CompanyContactBlock
    \else\ifnum\pdfstrcmp{#1}{header}=0
        \CompanyHeaderBlock{}
    \else\ifnum\pdfstrcmp{#1}{footer}=0
        \CompanyFooterBlock
    \else\ifnum\pdfstrcmp{#1}{simple}=0
        \CompanySimpleLine
    \else
        % Alapértelmezett: hivatalos blokk
        \CompanyOfficialBlock
    \fi\fi\fi\fi\fi
}

% ===== GYAKRAN HASZNÁLT RÖVIDÍTÉSEK =====
\newcommand{\kallab}{Kalibrálólaboratórium}
\newcommand{\iso}{MSZ EN ISO/IEC 17025:2018}
\newcommand{\nah}{Nemzeti Akkreditáló Hatóság}
\newcommand{\nahszam}{NAH-2-MINTA/2025}

% ===== TCOLORBOX STÍLUSOK =====
\tcbset{
    % [INFO] - Kiegészítő információk
    nahinfo/.style={
        colback=blue!8,
        colframe=blue!60!black,
        boxrule=1.2pt,
        arc=2mm,
        left=5mm, right=5mm, top=3mm, bottom=3mm,
        fonttitle=\bfseries,
        colbacktitle=blue!60!black,
        coltitle=white
    },
    % [KÖV] - Kötelező követelmények
    nahreq/.style={
        colback=green!8,
        colframe=green!70!black,
        boxrule=1.5pt,
        arc=2mm,
        left=5mm, right=5mm, top=3mm, bottom=3mm,
        fonttitle=\bfseries,
        colbacktitle=green!70!black,
        coltitle=white
    },
    % [FIGY] - Kritikus figyelmeztetések
    nahalert/.style={
        colback=red!8,
        colframe=red!70!black,
        boxrule=1.5pt,
        arc=2mm,
        left=5mm, right=5mm, top=3mm, bottom=3mm,
        fonttitle=\bfseries,
        colbacktitle=red!70!black,
        coltitle=white
    },
    % [VAL] - Validálás, ellenőrzés
    nahvalid/.style={
        colback=orange!10,
        colframe=orange!70!black,
        boxrule=1.2pt,
        arc=2mm,
        left=5mm, right=5mm, top=3mm, bottom=3mm,
        fonttitle=\bfseries,
        colbacktitle=orange!70!black,
        coltitle=white
    },
    % [BIZ] - Biztonsági és titoktartási aspectusok
    nahsec/.style={
        colback=purple!8,
        colframe=purple!70!black,
        boxrule=1.3pt,
        arc=2mm,
        left=5mm, right=5mm, top=3mm, bottom=3mm,
        fonttitle=\bfseries,
        colbacktitle=purple!70!black,
        coltitle=white
    }
}

% ===== LÁBLÉC MAKRÓK =====
\newcommand{\SetDocumentFooter}[3]{%
    \fancyfoot[L]{\footnotesize \nahszam{} | #1}
    \fancyfoot[C]{\footnotesize v#2 | #3}
    % NOTE: \pageref{LastPage} requires lastpage package (line 98)
    % LaTeX must be run TWICE for correct page numbers
    \fancyfoot[R]{\footnotesize \thepage/\pageref{LastPage}}
}

\newcommand{\SetMainFooter}{%
    \SetDocumentFooter{ISO17025-MK-01}{1.0}{2025.09.15}
}

\newcommand{\SetChapterFooter}[1]{%
    \SetDocumentFooter{ISO17025-CH#1}{1.0}{2025.09.15}
}

\newcommand{\SetAppendixFooter}[1]{%
    \SetDocumentFooter{#1}{1.0}{2025.09.15}
}

% ===== FEJLÉC ÉS LÁBLÉC BEÁLLÍTÁSOK =====
\pagestyle{fancy}
\fancyhf{}

\if@petitan@standalone
    % Standalone dokumentumok egyszerűbb fejléce
    \fancyhead[L]{\petitan}
    \fancyhead[R]{\iso}
\else
    % Kétoldalas dokumentumok fejléce
    \fancyhead[LE]{\petitan}
    \fancyhead[RO]{\iso}
\fi

\SetMainFooter
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}

% Fejezet kezdő oldalak stílusa
\fancypagestyle{chapter}{
    \fancyhf{}
    \SetMainFooter
    \renewcommand{\headrulewidth}{0pt}
    \renewcommand{\footrulewidth}{0.4pt}
}

% ===== FEJEZET FORMÁZÁS =====
\if@petitan@standalone
    % Standalone dokumentumokban nincs chapter
\else
    \titleformat{\chapter}[display]
        {\normalfont\huge\bfseries}
        {\thechapter. Fejezet}
        {20pt}
        {\Huge}
    \titlespacing*{\chapter}{0pt}{0pt}{40pt}
\fi

% ===== TARTALOMJEGYZÉK TESTRESZABÁS =====
\renewcommand{\cfttoctitlefont}{\hfill\Large\bfseries}
\renewcommand{\cftaftertoctitle}{\hfill}
\renewcommand{\cftlottitlefont}{\hfill\Large\bfseries}
\renewcommand{\cftafterlottitle}{\hfill}
\renewcommand{\cftloftitlefont}{\hfill\Large\bfseries}
\renewcommand{\cftafterloftitle}{\hfill}

% ===== HYPERREF BEÁLLÍTÁSOK =====
\hypersetup{
    colorlinks=true,
    linkcolor=petitanblue,
    filecolor=petitanblue,
    urlcolor=petitanblue,
    citecolor=petitanblue,
    pdfauthor={\petitan},
    pdfsubject={ISO 17025:2018 Minőségirányítási dokumentum},
    pdfkeywords={ISO 17025, kalibrálás, akkreditáció, minőségirányítás},
    pdftitle={PeTitan Kft. Minőségirányítási dokumentum},
    pdfcreator={LaTeX with petitanmk class}
}

% ===== VALIDÁLÁSI ÉS DOKUMENTUM MAKRÓK =====

% Validálási blokk teljes verzió
\newcommand{\ValidationBlock}[7]{%
    \subsection*{VALIDÁLÁS ÉS JÓVÁHAGYÁS}

    \begin{table}[!htbp]
    \centering
    \caption{Eljárás validálási információk}
    \begin{tabular}{|p{4cm}|p{11cm}|}
    \hline
    \textbf{Paraméter} & \textbf{Érték} \\
    \hline
    Készítette & #1 \\
    \hline
    Ellenőrizte & #2 \\
    \hline
    Jóváhagyta & #3 \\
    \hline
    Hatályba lépés & #4 \\
    \hline
    Következő felülvizsgálat & #5 \\
    \hline
    Verzió & #6 \\
    \hline
    Módosítások & #7 \\
    \hline
    \end{tabular}
    \end{table}

    \vfill

    \noindent
    \textbf{Készítette:} \makebox[5cm]{\hrulefill} \hspace{2cm} \textbf{Dátum:} \makebox[3cm]{\hrulefill}\\
    \hspace{1.5cm}{\small #1}

    \vspace{1cm}

    \noindent
    \textbf{Ellenőrizte:} \makebox[5cm]{\hrulefill} \hspace{2cm} \textbf{Dátum:} \makebox[3cm]{\hrulefill}\\
    \hspace{1.5cm}{\small #2}

    \vspace{1cm}

    \noindent
    \textbf{Jóváhagyta:} \makebox[5cm]{\hrulefill} \hspace{2cm} \textbf{Dátum:} \makebox[3cm]{\hrulefill}\\
    \hspace{1.5cm}{\small #3}

    \vspace{0.5cm}
}

% Egyszerűsített validálási blokk
\newcommand{\SimpleValidationBlock}[3]{%
    \vfill

    \noindent
    \textbf{Készítette:} \makebox[5cm]{\hrulefill} \hspace{2cm} \textbf{Dátum:} \makebox[3cm]{\hrulefill}\\
    \hspace{1.5cm}{\small #1}

    \vspace{1cm}

    \noindent
    \textbf{Ellenőrizte:} \makebox[5cm]{\hrulefill} \hspace{2cm} \textbf{Dátum:} \makebox[3cm]{\hrulefill}\\
    \hspace{1.5cm}{\small #2}

    \vspace{1cm}

    \noindent
    \textbf{Jóváhagyta:} \makebox[5cm]{\hrulefill} \hspace{2cm} \textbf{Dátum:} \makebox[3cm]{\hrulefill}\\
    \hspace{1.5cm}{\small #3}

    \vspace{0.5cm}
}

% Melléklet záró blokk
\newcommand{\AppendixEnd}[1]{%
    \begin{center}
    \textbf{--- #1. MELLÉKLET VÉGE ---}
    \end{center}
}

% Tervezett melléklet jelzés
\newcommand{\PlannedAppendixNotice}[2]{%
    \begin{tcolorbox}[colback=yellow!10,colframe=orange!50!black,title={\textbf{TERVEZETT MELLÉKLET}}]
    \textbf{Státusz:} KIDOLGOZÁS ALATT \\
    \textbf{Tervezett befejezés:} #1 \\
    \textbf{Hivatkozó szakasz:} #2
    \end{tcolorbox}
}

% Dokumentum fejléc táblázat
\newcommand{\DocumentHeader}[6]{%
    \noindent
    \begin{tabular}{|p{4cm}|p{11.5cm}|}
    \hline
    \textbf{Eljárás kódja:} & #1 \\
    \hline
    \textbf{Eljárás címe:} & #2 \\
    \hline
    \textbf{Alkalmazási terület:} & #3 \\
    \hline
    \textbf{Verzió:} & #4 \\
    \hline
    \textbf{Hatályba lépés:} & #5 \\
    \hline
    \textbf{Hivatkozások:} & #6 \\
    \hline
    \textbf{Jóváhagyta:} & Laboratóriumvezető \\
    \hline
    \end{tabular}

    \vspace{1cm}
}

% Melléklet cím blokk
\newcommand{\AppendixTitle}[3]{%
    \if@petitan@standalone
        % Standalone dokumentumokban nem kell cleardoublepage
    \else
        \cleardoublepage
        \section*{#1. MELLÉKLET}
        \addcontentsline{toc}{section}{#1. melléklet - #2}
    \fi

    % Lábléc beállítása
    \SetAppendixFooter{#1}

    \begin{center}
        \textbf{\Large #2}\\
        \vspace{0.5cm}
        \textbf{\large #3}
    \end{center}

    \vspace{0.5cm}
}

% Változáskezelési táblázat
\newcommand{\ChangeLog}{%
    \subsection*{VÁLTOZÁSOK JEGYZÉKE}

    \begin{table}[!htbp]
    \centering
    \caption{Dokumentum változások}
    \begin{tabular}{|p{2cm}|p{3cm}|p{10cm}|}
    \hline
    \textbf{Verzió} & \textbf{Dátum} & \textbf{Változás leírása} \\
    \hline
    1.0 & 2025.09.18 & Első kiadás, teljes dokumentum létrehozása \\
    \hline
    \end{tabular}
    \end{table}
}

% ===== KALIBRÁLÁSI ELJÁRÁS SPECIFIKUS MAKRÓK =====

% Környezeti paraméterek táblázat
\newcommand{\EnvironmentalConditions}[1]{%
    \subsection*{6.1 Környezeti feltételek}

    \begin{table}[h]
    \centering
    \caption{Környezeti paraméterek}
    \begin{tabular}{|p{4cm}|p{3cm}|p{6cm}|}
    \hline
    \textbf{Paraméter} & \textbf{Tartomány} & \textbf{Megjegyzés} \\
    \hline
    #1
    \hline
    \end{tabular}
    \end{table}
}

% Bizonytalansági komponens táblázat
\newcommand{\UncertaintyTable}[3]{%
    \begin{table}[h]
    \centering
    \caption{#1}
    \footnotesize
    \begin{tabular}{|p{3.5cm}|p{2cm}|p{1.5cm}|p{1.5cm}|p{1.2cm}|p{1.5cm}|}
    \hline
    \textbf{Bizonytalansági forrás} & \textbf{Becsült érték} & \textbf{Eloszlás} & \textbf{Osztó} & \textbf{u($x_i$)} & \textbf{$c_i \cdot u$} \\
    & #2 & & & #2 & #2 \\
    \hline
    #3
    \hline
    \end{tabular}
    \end{table}
}

% Kalibrálási pontok táblázat
\newcommand{\CalibrationPoints}[2]{%
    \subsection*{8.1 Kalibrálási pontok}

    \begin{table}[h]
    \centering
    \caption{#1}
    \begin{tabular}{|c|c|c|c|}
    \hline
    \textbf{Pont} & \textbf{Névleges érték} & \textbf{Mért érték} & \textbf{Hiba} \\
    \hline
    #2
    \hline
    \end{tabular}
    \end{table}
}

% ===== DOKUMENTUM TÍPUS SPECIFIKUS BEÁLLÍTÁSOK =====
\AtBeginDocument{%
    \if@petitan@main
        % Fő kézikönyv specifikus beállítások
        \SetMainFooter
    \fi

    \if@petitan@chapter
        % Fejezet specifikus beállítások
        \SetChapterFooter{01}
    \fi

    \if@petitan@appendix
        % Melléklet specifikus beállítások
        \SetAppendixFooter{A}
    \fi

    \if@petitan@procedure
        % Eljárás specifikus beállítások
        \SetAppendixFooter{ME-01}
    \fi

    \if@petitan@standalone
        % Standalone specifikus beállítások
        \SetAppendixFooter{STANDALONE}
        % Egyoldalas layout
        \geometry{margin=2cm}
    \fi
}

% ===== MATEMATIKAI KÖRNYEZETEK =====
% Tételek, definíciók, példák támogatása

\RequirePackage{amsthm}

\newtheorem{theorem}{Tétel}[section]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{proposition}[theorem]{Állítás}
\newtheorem{corollary}[theorem]{Következmény}

\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definíció}
\newtheorem{example}[theorem]{Példa}

\theoremstyle{remark}
\newtheorem{remark}[theorem]{Megjegyzés}

% ===== KÓD BLOKKOK TÁMOGATÁSA =====
% Listings csomag konfiguráció

\RequirePackage{listings}

\lstset{
    basicstyle=\ttfamily\small,
    breaklines=true,
    frame=single,
    numbers=left,
    numberstyle=\tiny\color{gray},
    showstringspaces=false,
    commentstyle=\color{green!50!black},
    keywordstyle=\color{blue},
    stringstyle=\color{red!70!black},
    tabsize=4,
    captionpos=b
}

% UTF-8 támogatás listingshez (magyar karakterek)
\lstset{
    literate=%
    {á}{{\'a}}1 {é}{{\'e}}1 {í}{{\'i}}1 {ó}{{\'o}}1 {ö}{{\"o}}1 {ő}{{\H{o}}}1 {ú}{{\'u}}1 {ü}{{\"u}}1 {ű}{{\H{u}}}1
    {Á}{{\'A}}1 {É}{{\'E}}1 {Í}{{\'I}}1 {Ó}{{\'O}}1 {Ö}{{\"O}}1 {Ő}{{\H{O}}}1 {Ú}{{\'U}}1 {Ü}{{\"U}}1 {Ű}{{\H{U}}}1
}

% ===== v2.2.3 (Issue #3) - EMBEDDED MODE: NUMERIC APPENDIX NUMBERING =====
% When embedded as appendix in main QMS manual, use numeric numbering instead of alphabetic
% This allows scaling beyond 26 appendices and follows ISO 17025 best practices
\if@petitan@embedded
    % Numeric appendix numbering instead of alphabetic (A, B, C... → 1, 2, 3...)
    \renewcommand{\appendix}{%
        \setcounter{chapter}{0}%
        \renewcommand{\thechapter}{\arabic{chapter}}%
        \renewcommand{\chaptername}{Melléklet}%
        \renewcommand{\thesection}{\thechapter.\arabic{section}}%
    }
\fi

% ===== OSZTÁLY VÉGE =====
\endinput
