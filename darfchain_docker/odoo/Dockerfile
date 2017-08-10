FROM debian:jessie
MAINTAINER Odoo S.A. <info@odoo.com>

# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
RUN set -x; \
        apt-get update \
        && apt-get install -y --no-install-recommends \
            ca-certificates \
            curl \
            node-less \
            python-gevent \
            python-pip \
            python-renderpm \
            python-support \
            python-watchdog \
            python3 \
            python3-pip\
            build-essential \
            autoconf \
            libtool \
            pkg-config \
            python-opengl \
            python-imaging \
            python-pyrex \
            python-pyside.qtopengl \
            idle-python2.7 \
            qt4-dev-tools \
            qt4-designer \
            libqtgui4 \
            libqtcore4 \
            libqt4-xml \
            libqt4-test \
            libqt4-script \
            libqt4-network \
            libqt4-dbus \
            python-qt4 \
            python-qt4-gl \
            libgle3 \
            python-dev \
            python3-dev \ 
            libffi-dev \
            libssl-dev \
        && curl -o wkhtmltox.deb -SL http://nightly.odoo.com/extra/wkhtmltox-0.12.1.2_linux-jessie-amd64.deb \
        && echo '40e8b906de658a2221b15e4e8cd82565a47d7ee8 wkhtmltox.deb' | sha1sum -c - \
        && dpkg --force-depends -i wkhtmltox.deb \
        && apt-get -y install -f --no-install-recommends \
        && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false -o APT::AutoRemove::SuggestsImportant=false npm \
        && rm -rf /var/lib/apt/lists/* wkhtmltox.deb \
        && pip install psycogreen==1.0 \
        && pip install xmltodict \
        && pip install rethinkdb \ 
        && pip install base58 \
        && pip install pywaves \
        && pip3 install bigchaindb_driver


# Install Odoo
ENV ODOO_VERSION 10.0
ENV ODOO_RELEASE 20170207
RUN set -x; \
        curl -o odoo.deb -SL http://nightly.odoo.com/${ODOO_VERSION}/nightly/deb/odoo_${ODOO_VERSION}.${ODOO_RELEASE}_all.deb \
        && echo '5d2fb0cc03fa0795a7b2186bb341caa74d372e82 odoo.deb' | sha1sum -c - \
        && dpkg --force-depends -i odoo.deb \
        && apt-get update \
        && apt-get -y install -f --no-install-recommends \
        && rm -rf /var/lib/apt/lists/* odoo.deb

# Copy entrypoint script and Odoo configuration file
COPY ./entrypoint.sh /
COPY ./odoo.conf /etc/odoo/
COPY ./putbigchaindb.py /usr/bin/
RUN chown odoo /etc/odoo/odoo.conf

# Mount /var/lib/odoo to allow restoring filestore and /mnt/extra-addons for users addons
RUN mkdir -p /mnt/extra-addons \
        && chown -R odoo /mnt/extra-addons
VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]
# Expose Odoo services
EXPOSE 8069 8078

# Set the default config file
ENV ODOO_RC /etc/odoo/odoo.conf

# Set default user when running the container
USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
