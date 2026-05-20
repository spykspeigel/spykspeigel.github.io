\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{res}[2026/05/20 Local resume class compatibility layer]

\LoadClass[11pt]{article}

\setlength{\parindent}{0pt}
\setlength{\parskip}{4pt}

\makeatletter
\newcommand{\@resname}{}
\newcommand{\@resaddresses}{}

\newcommand{\name}[1]{\gdef\@resname{#1}}
\newcommand{\address}[1]{%
  \g@addto@macro\@resaddresses{\par #1}%
}

\newenvironment{resume}{%
  \begin{center}
    {\Large\bfseries \@resname\par}
    \vspace{3pt}
    {\small \@resaddresses\par}
  \end{center}
  \vspace{4pt}
}{}

\renewcommand{\section}[1]{%
  \par\vspace{8pt}%
  {\large\bfseries #1\par}%
  \vspace{2pt}%
}
\makeatother
