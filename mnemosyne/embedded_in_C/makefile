CC	= gcc
CFLAGS	= -O -I/usr/include/python2.6
LD	= $(CC)
LDFLAGS	= -lpython2.6
RM	= rm

EXE	= mnemosyne
SRCS = python_bridge.c main_wdgt.c review_wdgt.c dlgs.c python_stdout_stderr.c \
	example_client.c 
OBJS = ${SRCS:.c=.o}

.c.o :
	$(CC) $(CFLAGS) -c $<

all : $(EXE)

$(EXE) : $(OBJS)
	$(LD) $(LDFLAGS) -o $@ $(OBJS)

$(OBJS) : python_bridge.h main_wdgt.h review_wdgt.h dlgs.h python_stdout_stderr.h

clean :
	-$(RM) -f $(EXE) $(OBJS)
