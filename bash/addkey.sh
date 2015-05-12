#!/bin/sh

#create HOME/.ssh dir if not existed
if [ ! -d ~/.ssh ]; then
    mkdir -p ~/.ssh;
    chmod 700 ~/.ssh;
fi

#add new line to the end if not present
if [ -f ~/.ssh/authorized_keys ]; then
    if [ "`tail -c 1 ~/.ssh/authorized_keys`" != "" ]; then
        echo "" >> ~/.ssh/authorized_keys;
    fi
fi

#add ssh pub key
cat >> ~/.ssh/authorized_keys << EOF
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDEb5v2wjLeL2M8CCwqSC/cd2POTyyPx5ppL/TrFUlVdGxclN+D9rz2OZWQblkTz9d05N7P7vdNEyhdMZxlXHQ6SIZnvJet0cX/kDoFn7sGxI3ppIPiRtzdEaSHaplIy62fs1jBegOoByjJ0AddgS39mPA5qrv/sz6dbWSDlXvQzJ1HlenopYZmVrwo3vNU2xdU1tZFiHikF7i2s0agnHuu71NdthZNez3hhjpaWVUfqAKNq6c6+gpXCFkevnm9zrGbiHL79s+xjjzL7Ef+Rjznh9kPPgFgONN7cNF+gIqd7OHgFSP6fF/Z9WIGz7IvB5nEPAEb46X+HCQyYQB2cuq/ boypt@pt-laptop
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC2SFtarNKZjpHBQOZi5SV1Tounlz9V6dgt02trOta6hlIbLFMI9OFZZUQHKhvx4/JTZHoDkcOMpqlf38XO/i1ejnE7VZXaNFhKyKno+RfXxbBmXdqlG43M2lK/Go1FOZTUfRdN31HFjWntP3SX9TTOFc9KGUhRDE/LqxNvCVQ/e1GTVYIK8AihmKKqDaZilEVkEzTllYWcLluJRBkmKPcXCvhK1dHHPRNtDzVRAeEtxS4xn40Q65Dp/tXUnNs8zjoTvA9H3HU8gjr4gA5usaXsNUSp4amGNzbUZPDFTOzzwM51uRD+8Xe5p54rJeg2Y9xdQYMbkaH6uj+drl3DM9kP boypt@pt-drcom-desk
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDHz+h5X2lpl/mO/q6rbAwNYNNyZAt8htvpcKn+lzMdvaKzww/douKIjtDNEqe8oihYvuMCCoIyfi7Rx3eEnVL6HP4rVn+K7NUdpXR0YJ2urJpaOjM9hVPrSKo9pu6zozAoi9YRMduaRDNq0sNZdHFHFYXThYsj6aNZgd/KWluOXpVAS3Szi/6iaNfDrSKfRf0Y9hML7do71F7ywpxMW+qVZTM9jJwMqdOxZsSZZeLsg88vBYiyyTUdc2ImD1jA7pS3pbEw8ZbdXC0uCG8CcIkKc0oecN5X3HyjClNNXKo4wgXbH27+6vpA5fOm5NHA0Qd9xFvfYDAjGdEkemeCG8rJ JuiceSSH-idnt
EOF

#secure mod
chmod 600 ~/.ssh/authorized_keys;

echo "Done Adding Keys."

